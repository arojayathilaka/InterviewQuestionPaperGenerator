from .base_agent import BaseAgent
from typing import List, Optional, Any
from app.config import settings


class QuestionGeneratorAgent(BaseAgent):
    """Generates questions based on topic analysis"""
    
    async def execute(
        self,
        topic: str,
        subtopics: List[str],
        num_questions: int,
        question_types: List[str],
        difficulty_level: str
    ) -> List[dict]:
        """
        Generate questions for the given topic
        
        Args:
            topic: Main technology topic
            subtopics: Subtopics to generate questions from
            num_questions: Number of questions to generate
            question_types: Types of questions (multiple_choice, short_answer, etc.)
            difficulty_level: Overall difficulty level (easy, medium, hard, mixed)
            
        Returns:
            List of generated questions with metadata
        """
        if settings.AI_PROVIDER == "anthropic":
            return await self._execute_anthropic(
                topic, subtopics, num_questions, question_types, difficulty_level
            )
        else:
            return await self._execute_openai(
                topic, subtopics, num_questions, question_types, difficulty_level
            )
    
    async def _execute_anthropic(
        self,
        topic: str,
        subtopics: List[str],
        num_questions: int,
        question_types: List[str],
        difficulty_level: str
    ) -> List[dict]:
        """Execute using Anthropic Claude"""
        try:
            from anthropic import AsyncAnthropic
            
            client = AsyncAnthropic(api_key=self.api_key)
            
            subtopics_str = ", ".join(subtopics)
            question_types_str = ", ".join(question_types)
            
            prompt = f"""Generate {num_questions} interview questions for {topic}.

Subtopics: {subtopics_str}
Question Types: {question_types_str}
Difficulty Level: {difficulty_level}

Return a JSON array with each question having:
- question_text: The question content
- options: Array of options (for multiple choice)
- correct_answer: The correct answer
- difficulty_level: easy/medium/hard
- topic: The subtopic this question covers
- explanation: Brief explanation of the answer

Return only valid JSON array."""

            message = await client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            parsed = self._parse_json_response(f"[{response_text}]" if response_text.startswith("{") else response_text)
            
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict) and "questions" in parsed:
                return parsed["questions"]
            else:
                return [parsed] if isinstance(parsed, dict) else []
            
        except Exception as e:
            raise Exception(f"QuestionGeneratorAgent execution failed: {str(e)}")
    
    async def _execute_openai(
        self,
        topic: str,
        subtopics: List[str],
        num_questions: int,
        question_types: List[str],
        difficulty_level: str
    ) -> List[dict]:
        """Execute using OpenAI GPT"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.api_key)
            
            subtopics_str = ", ".join(subtopics)
            question_types_str = ", ".join(question_types)
            
            prompt = f"""Generate {num_questions} interview questions for {topic}.

Subtopics: {subtopics_str}
Question Types: {question_types_str}
Difficulty Level: {difficulty_level}

Return a JSON array with each question having:
- question_text: The question content
- options: Array of options (for multiple choice)
- correct_answer: The correct answer
- difficulty_level: easy/medium/hard
- topic: The subtopic this question covers
- explanation: Brief explanation of the answer

Return only valid JSON array."""

            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4096
            )
            
            response_text = response.choices[0].message.content
            parsed = self._parse_json_response(f"[{response_text}]" if response_text.startswith("{") else response_text)
            
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict) and "questions" in parsed:
                return parsed["questions"]
            else:
                return [parsed] if isinstance(parsed, dict) else []
            
        except Exception as e:
            raise Exception(f"QuestionGeneratorAgent execution failed: {str(e)}")
