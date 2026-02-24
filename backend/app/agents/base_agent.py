from abc import ABC, abstractmethod
from typing import List, Optional, Any
import asyncio
import json
from tenacity import retry, stop_after_attempt, wait_exponential


class BaseAgent(ABC):
    """Base class for all AI agents with retry logic"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the agent's task"""
        pass
    
    def _parse_json_response(self, response: str) -> dict:
        """Parse JSON from model response with fallback"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                try:
                    return json.loads(response[start:end])
                except json.JSONDecodeError:
                    return {"raw": response}
            return {"raw": response}
