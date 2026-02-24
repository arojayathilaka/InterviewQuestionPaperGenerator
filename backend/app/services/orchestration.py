import asyncio
import json
from typing import Optional, List
from uuid import uuid4
import logging

from app.config import settings
from app.agents import (
    TopicAnalyzerAgent,
    QuestionGeneratorAgent,
    DifficultyCalibratorAgent,
    PaperFormatterAgent,
)
from app.services import (
    get_service_bus_service,
    get_cosmos_db_service,
    get_blob_storage_service,
)
from app.models import PaperGenerationRequest, PaperGenerationResponse, QuestionItem
from app.utils import (
    PaperGenerationError,
    AIAgentError,
    AzureServiceError,
    get_logger,
    generate_paper_id,
    get_current_timestamp,
    calculate_difficulty_distribution,
)

logger = get_logger(__name__)


class PaperOrchestrationService:
    """Orchestrates the paper generation workflow using AI agents and Azure services"""
    
    def __init__(self):
        # Initialize AI agents
        api_key = (
            settings.OPENAI_API_KEY
            if settings.AI_PROVIDER == "openai"
            else settings.ANTHROPIC_API_KEY
        )
        
        self.topic_analyzer = TopicAnalyzerAgent(api_key, settings.AI_MODEL)
        self.question_generator = QuestionGeneratorAgent(api_key, settings.AI_MODEL)
        self.difficulty_calibrator = DifficultyCalibratorAgent(api_key, settings.AI_MODEL)
        self.paper_formatter = PaperFormatterAgent(api_key, settings.AI_MODEL)
    
    async def generate_paper(self, request: PaperGenerationRequest) -> str:
        """
        Orchestrate paper generation workflow
        
        Args:
            request: Paper generation request
            
        Returns:
            Paper ID
        """
        paper_id = generate_paper_id()
        logger.info(f"Starting paper generation: {paper_id} for user {request.user_id}")
        
        try:
            # Create paper metadata in Cosmos DB with initial status
            cosmos_db = await get_cosmos_db_service()
            paper_metadata = {
                "id": paper_id,
                "user_id": request.user_id,
                "topic": request.technology_topic,
                "status": "queued",
                "num_questions": request.num_questions,
                "difficulty_level": request.difficulty_level,
                "question_types": request.question_types or [],
                "duration_minutes": request.duration_minutes,
                "created_at": get_current_timestamp(),
                "updated_at": get_current_timestamp(),
                "progress": 0,
            }
            
            await cosmos_db.create_user(paper_id, paper_metadata)
            logger.info(f"Paper metadata created: {paper_id}")
            
            # Send to Service Bus for async processing
            service_bus = await get_service_bus_service()
            await service_bus.send_message(
                message_body={
                    "paper_id": paper_id,
                    "request": request.dict(),
                },
                message_id=paper_id,
                properties={
                    "user_id": request.user_id,
                    "topic": request.technology_topic,
                    "status": "queued",
                }
            )
            
            logger.info(f"Paper generation queued: {paper_id}")
            return paper_id
            
        except Exception as e:
            logger.error(f"Failed to queue paper generation: {e}")
            raise AzureServiceError(
                f"Failed to queue paper generation",
                "ServiceBus",
                {"paper_id": paper_id, "error": str(e)}
            )
    
    async def execute_paper_generation(self, paper_id: str, request_dict: dict) -> bool:
        """
        Execute the actual paper generation workflow
        
        Args:
            paper_id: Paper ID
            request_dict: Request data as dictionary
            
        Returns:
            True if generation successful
        """
        cosmos_db = None
        request = None
        paper_url = None
        calibrated_questions = []
        difficulty_dist = {}
        try:
            logger.info(f"Executing paper generation workflow: {paper_id}")
            # Parse request
            request = PaperGenerationRequest(**request_dict)
            # Step 1: Analyze topic
            logger.info(f"[{paper_id}] Step 1: Analyzing topic")
            try:
                topic_analysis = await self.topic_analyzer.execute(
                    topic=request.technology_topic,
                    num_questions=request.num_questions,
                    preferences=request.preferences
                )
            except Exception as e:
                raise AIAgentError(
                    f"Topic analysis failed: {str(e)}",
                    "TopicAnalyzerAgent",
                    {"paper_id": paper_id}
                )
            subtopics = topic_analysis.get("main_subtopics", [])
            difficulty_spread = topic_analysis.get("difficulty_spread", {})
            # Step 2: Generate questions
            logger.info(f"[{paper_id}] Step 2: Generating questions")
            try:
                questions = await self.question_generator.execute(
                    topic=request.technology_topic,
                    subtopics=subtopics,
                    num_questions=request.num_questions,
                    question_types=request.question_types,
                    difficulty_level=request.difficulty_level
                )
            except Exception as e:
                raise AIAgentError(
                    f"Question generation failed: {str(e)}",
                    "QuestionGeneratorAgent",
                    {"paper_id": paper_id}
                )
            # Step 3: Calibrate difficulty
            logger.info(f"[{paper_id}] Step 3: Calibrating difficulty levels")
            try:
                calibrated_questions = await self.difficulty_calibrator.execute(
                    questions=questions,
                    difficulty_distribution=difficulty_spread,
                    target_level=request.difficulty_level
                )
            except Exception as e:
                logger.warning(f"Difficulty calibration warning: {e}")
                calibrated_questions = questions
            # Step 4: Format paper
            logger.info(f"[{paper_id}] Step 4: Formatting paper")
            try:
                formatted_paper = await self.paper_formatter.execute(
                    topic=request.technology_topic,
                    questions=calibrated_questions,
                    duration_minutes=request.duration_minutes,
                    paper_title=f"Interview Questions: {request.technology_topic}"
                )
            except Exception as e:
                raise AIAgentError(
                    f"Paper formatting failed: {str(e)}",
                    "PaperFormatterAgent",
                    {"paper_id": paper_id}
                )
            # Calculate difficulty distribution
            difficulty_dist = self._calculate_difficulty_distribution(calibrated_questions)
            # Step 5: Store paper in Blob Storage
            logger.info(f"[{paper_id}] Step 5: Storing paper in Blob Storage")
            try:
                blob_storage = await get_blob_storage_service()
                paper_blob_name = f"papers/{paper_id}/paper.json"
                paper_content = {
                    "paper_id": paper_id,
                    "topic": request.technology_topic,
                    "created_at": get_current_timestamp(),
                    "questions": calibrated_questions,
                    "difficulty_distribution": difficulty_dist,
                    "formatted_content": formatted_paper,
                    "duration_minutes": request.duration_minutes,
                }
                paper_url = await blob_storage.upload_paper(
                    blob_name=paper_blob_name,
                    paper_content=paper_content,
                    metadata={
                        "paper_id": paper_id,
                        "user_id": request.user_id,
                        "topic": request.technology_topic,
                    }
                )
            except Exception as e:
                raise AzureServiceError(
                    f"Failed to store paper in Blob Storage: {str(e)}",
                    "BlobStorage",
                    {"paper_id": paper_id}
                )
            # Step 6: Store metadata in Cosmos DB
            logger.info(f"[{paper_id}] Step 6: Storing metadata in Cosmos DB")
            try:
                cosmos_db = await get_cosmos_db_service()
                # Update paper record with completion status
                await cosmos_db.update_item_field(
                    item_id=paper_id,
                    field_name="status",
                    field_value="completed"
                )
                await cosmos_db.update_item_field(
                    item_id=paper_id,
                    field_name="paper_url",
                    field_value=paper_url
                )
                await cosmos_db.update_item_field(
                    item_id=paper_id,
                    field_name="questions_count",
                    field_value=len(calibrated_questions)
                )
                await cosmos_db.update_item_field(
                    item_id=paper_id,
                    field_name="difficulty_distribution",
                    field_value=difficulty_dist
                )
                await cosmos_db.update_item_field(
                    item_id=paper_id,
                    field_name="progress",
                    field_value=100
                )
                # Update user papers count
                user_profile = await cosmos_db.get_user(request.user_id)
                if user_profile:
                    user_profile["papers_generated"] = user_profile.get("papers_generated", 0) + 1
                    await cosmos_db.create_user(request.user_id, user_profile)
            except Exception as e:
                logger.warning(f"Failed to store metadata in Cosmos DB: {e}")
            logger.info(f"[{paper_id}] Paper generation completed successfully")
            return True
        except PaperGenerationError:
            raise
        except AIAgentError:
            raise
        except AzureServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in paper generation: {e}")
            raise PaperGenerationError(
                f"Paper generation workflow failed: {str(e)}",
                "workflow_execution",
                {"paper_id": paper_id}
            )
        finally:
            # Guarantee status update to 'completed' if possible, and log errors
            try:
                if cosmos_db is None:
                    cosmos_db = await get_cosmos_db_service()
                await cosmos_db.update_item_field(
                    item_id=paper_id,
                    field_name="status",
                    field_value="completed"
                )
            except Exception as final_update_err:
                logger.error(f"[GUARANTEE] Failed to set status to 'completed' for {paper_id}: {final_update_err}")
    
    def _calculate_difficulty_distribution(self, questions: List[dict]) -> dict:
        """Calculate difficulty distribution from questions"""
        distribution = {"easy": 0, "medium": 0, "hard": 0}
        
        for question in questions:
            difficulty = question.get("difficulty_level", "medium").lower()
            if difficulty in distribution:
                distribution[difficulty] += 1
        
        return distribution


# Singleton instance
_orchestration_service: Optional[PaperOrchestrationService] = None


async def get_orchestration_service() -> PaperOrchestrationService:
    """Get or create orchestration service instance"""
    global _orchestration_service
    if _orchestration_service is None:
        _orchestration_service = PaperOrchestrationService()
    return _orchestration_service
