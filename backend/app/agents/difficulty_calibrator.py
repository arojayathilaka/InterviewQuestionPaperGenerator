from .base_agent import BaseAgent
from typing import List, Optional, Any
from app.config import settings


class DifficultyCalibratorAgent(BaseAgent):
    """Calibrates and distributes difficulty levels across questions"""
    
    async def execute(
        self,
        questions: List[dict],
        difficulty_distribution: Optional[dict] = None,
        target_level: str = "mixed"
    ) -> List[dict]:
        """
        Calibrate difficulty levels of questions
        
        Args:
            questions: List of generated questions
            difficulty_distribution: Target distribution (e.g., {"easy": 0.3, "medium": 0.5, "hard": 0.2})
            target_level: Overall target difficulty level
            
        Returns:
            List of questions with calibrated difficulty levels
        """
        if settings.AI_PROVIDER == "anthropic":
            return await self._execute_anthropic(
                questions, difficulty_distribution, target_level
            )
        else:
            return await self._execute_openai(
                questions, difficulty_distribution, target_level
            )
    
    async def _execute_anthropic(
        self,
        questions: List[dict],
        difficulty_distribution: Optional[dict] = None,
        target_level: str = "mixed"
    ) -> List[dict]:
        """Execute using Anthropic Claude"""
        try:
            from anthropic import AsyncAnthropic
            import json
            
            client = AsyncAnthropic(api_key=self.api_key)
            
            distribution_str = json.dumps(difficulty_distribution or {
                "easy": 0.3,
                "medium": 0.5,
                "hard": 0.2
            })
            
            prompt = f"""Analyze and calibrate the difficulty levels of these interview questions.

Target difficulty distribution: {distribution_str}
Overall target level: {target_level}
Total questions: {len(questions)}

Questions:
{json.dumps(questions, indent=2)}

For each question, assign a calibrated difficulty_level (easy, medium, hard) ensuring the distribution matches the targets.
Return a JSON array with the questions, with updated difficulty_level fields.
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
            else:
                return questions  # Return original if parsing fails
            
        except Exception as e:
            raise Exception(f"DifficultyCalibratorAgent execution failed: {str(e)}")
    
    async def _execute_openai(
        self,
        questions: List[dict],
        difficulty_distribution: Optional[dict] = None,
        target_level: str = "mixed"
    ) -> List[dict]:
        """Execute using OpenAI GPT"""
        try:
            from openai import AsyncOpenAI
            import json
            
            client = AsyncOpenAI(api_key=self.api_key)
            
            distribution_str = json.dumps(difficulty_distribution or {
                "easy": 0.3,
                "medium": 0.5,
                "hard": 0.2
            })
            
            prompt = f"""Analyze and calibrate the difficulty levels of these interview questions.

Target difficulty distribution: {distribution_str}
Overall target level: {target_level}
Total questions: {len(questions)}

Questions:
{json.dumps(questions, indent=2)}

For each question, assign a calibrated difficulty_level (easy, medium, hard) ensuring the distribution matches the targets.
Return a JSON array with the questions, with updated difficulty_level fields.
Return only valid JSON array."""

            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=4096
            )
            
            response_text = response.choices[0].message.content
            parsed = self._parse_json_response(f"[{response_text}]" if response_text.startswith("{") else response_text)
            
            if isinstance(parsed, list):
                return parsed
            else:
                return questions  # Return original if parsing fails
            
        except Exception as e:
            raise Exception(f"DifficultyCalibratorAgent execution failed: {str(e)}")
