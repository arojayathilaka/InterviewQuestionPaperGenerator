from .base_agent import BaseAgent
from typing import List, Optional, Any
from app.config import settings


class PaperFormatterAgent(BaseAgent):
    """Formats questions into a professional question paper"""
    
    async def execute(
        self,
        topic: str,
        questions: List[dict],
        duration_minutes: int,
        paper_title: Optional[str] = None
    ) -> dict:
        """
        Format questions into a professional question paper
        
        Args:
            topic: Technology topic
            questions: List of questions to format
            duration_minutes: Exam duration in minutes
            paper_title: Optional custom paper title
            
        Returns:
            Dictionary with formatted paper content and metadata
        """
        if settings.AI_PROVIDER == "anthropic":
            return await self._execute_anthropic(
                topic, questions, duration_minutes, paper_title
            )
        else:
            return await self._execute_openai(
                topic, questions, duration_minutes, paper_title
            )
    
    async def _execute_anthropic(
        self,
        topic: str,
        questions: List[dict],
        duration_minutes: int,
        paper_title: Optional[str] = None
    ) -> dict:
        """Execute using Anthropic Claude"""
        try:
            from anthropic import AsyncAnthropic
            import json
            
            client = AsyncAnthropic(api_key=self.api_key)
            
            title = paper_title or f"Interview Question Paper: {topic}"
            
            prompt = f"""Create a professional formatted question paper from these questions.

Title: {title}
Duration: {duration_minutes} minutes
Topic: {topic}

Questions:
{json.dumps(questions, indent=2)}

Format the paper with:
1. Header with title, duration, and instructions
2. Questions numbered and organized by difficulty level
3. Space for answers
4. Instructions at the beginning
5. Answer key at the end with explanations

Return a JSON object with:
- formatted_paper: The full formatted text
- title: Paper title
- difficulty_distribution: Count of easy/medium/hard questions
- total_marks: Estimated marks (based on difficulty)
- instructions: Exam instructions

Return only valid JSON."""

            message = await client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            parsed = self._parse_json_response(response_text)
            
            return parsed if isinstance(parsed, dict) else {"formatted_paper": response_text}
            
        except Exception as e:
            raise Exception(f"PaperFormatterAgent execution failed: {str(e)}")
    
    async def _execute_openai(
        self,
        topic: str,
        questions: List[dict],
        duration_minutes: int,
        paper_title: Optional[str] = None
    ) -> dict:
        """Execute using OpenAI GPT"""
        try:
            from openai import AsyncOpenAI
            import json
            
            client = AsyncOpenAI(api_key=self.api_key)
            
            title = paper_title or f"Interview Question Paper: {topic}"
            
            prompt = f"""Create a professional formatted question paper from these questions.

Title: {title}
Duration: {duration_minutes} minutes
Topic: {topic}

Questions:
{json.dumps(questions, indent=2)}

Format the paper with:
1. Header with title, duration, and instructions
2. Questions numbered and organized by difficulty level
3. Space for answers
4. Instructions at the beginning
5. Answer key at the end with explanations

Return a JSON object with:
- formatted_paper: The full formatted text
- title: Paper title
- difficulty_distribution: Count of easy/medium/hard questions
- total_marks: Estimated marks (based on difficulty)
- instructions: Exam instructions

Return only valid JSON."""

            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=4096
            )
            
            response_text = response.choices[0].message.content
            parsed = self._parse_json_response(response_text)
            
            return parsed if isinstance(parsed, dict) else {"formatted_paper": response_text}
            
        except Exception as e:
            raise Exception(f"PaperFormatterAgent execution failed: {str(e)}")
