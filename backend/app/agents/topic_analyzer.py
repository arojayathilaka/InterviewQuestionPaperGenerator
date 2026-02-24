from .base_agent import BaseAgent
from typing import List, Optional, Any
from app.config import settings


class TopicAnalyzerAgent(BaseAgent):
    """Analyzes the technology topic and generates subtopics and key areas"""
    
    async def execute(
        self,
        topic: str,
        num_questions: int,
        preferences: Optional[str] = None
    ) -> dict:
        """
        Analyze a technology topic and break it into subtopics
        
        Args:
            topic: Technology topic (e.g., "Python Async Programming")
            num_questions: Number of questions to generate
            preferences: User preferences for the topic
            
        Returns:
            Dictionary with subtopics, key concepts, and focus areas
        """
        if settings.AI_PROVIDER == "anthropic":
            return await self._execute_anthropic(topic, num_questions, preferences)
        else:
            return await self._execute_openai(topic, num_questions, preferences)
    
    async def _execute_anthropic(
        self,
        topic: str,
        num_questions: int,
        preferences: Optional[str] = None
    ) -> dict:
        """Execute using Anthropic Claude"""
        try:
            from anthropic import AsyncAnthropic
            
            client = AsyncAnthropic(api_key=self.api_key)
            
            prompt = f"""Analyze the following technology topic and provide a structured breakdown:

Topic: {topic}
Number of Questions: {num_questions}
User Preferences: {preferences or 'None'}

Provide the analysis in JSON format with:
1. main_subtopics: List of 3-5 main subtopics
2. key_concepts: List of 5-10 key concepts to cover
3. focus_areas: List of specific areas to focus on
4. difficulty_spread: Suggested distribution of easy/medium/hard questions

Return only valid JSON."""

            message = await client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            return self._parse_json_response(response_text)
            
        except Exception as e:
            raise Exception(f"TopicAnalyzerAgent execution failed: {str(e)}")
    
    async def _execute_openai(
        self,
        topic: str,
        num_questions: int,
        preferences: Optional[str] = None
    ) -> dict:
        """Execute using OpenAI GPT"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.api_key)
            
            prompt = f"""Analyze the following technology topic and provide a structured breakdown:

Topic: {topic}
Number of Questions: {num_questions}
User Preferences: {preferences or 'None'}

Provide the analysis in JSON format with:
1. main_subtopics: List of 3-5 main subtopics
2. key_concepts: List of 5-10 key concepts to cover
3. focus_areas: List of specific areas to focus on
4. difficulty_spread: Suggested distribution of easy/medium/hard questions

Return only valid JSON."""

            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024
            )
            
            response_text = response.choices[0].message.content
            return self._parse_json_response(response_text)
            
        except Exception as e:
            raise Exception(f"TopicAnalyzerAgent execution failed: {str(e)}")
