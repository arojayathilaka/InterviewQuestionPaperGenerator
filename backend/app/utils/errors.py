from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Callable, Any, TypeVar, Optional
import asyncio
import logging
from functools import wraps

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


class RetryConfig:
    """Configuration for retry logic"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 10.0,
        exponential_base: float = 2.0,
        retry_on_exceptions: Optional[tuple] = None
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retry_on_exceptions = retry_on_exceptions or (Exception,)


def async_retry(config: Optional[RetryConfig] = None):
    """
    Decorator for async functions with retry logic
    
    Args:
        config: RetryConfig instance
        
    Returns:
        Decorated function with retry logic
    """
    if config is None:
        config = RetryConfig()
    
    return retry(
        stop=stop_after_attempt(config.max_attempts),
        wait=wait_exponential(
            multiplier=config.initial_delay,
            min=config.initial_delay,
            max=config.max_delay
        ),
        retry=retry_if_exception_type(config.retry_on_exceptions),
        reraise=True,
        before_sleep=lambda retry_state: logger.warning(
            f"Retry attempt {retry_state.attempt_number} for {retry_state.fn.__name__}"
        )
    )


class ApplicationError(Exception):
    """Base exception for application errors"""
    
    def __init__(self, message: str, error_code: str = "UNKNOWN", details: Optional[dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ApplicationError):
    """Validation error"""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class AzureServiceError(ApplicationError):
    """Azure service integration error"""
    
    def __init__(self, message: str, service_name: str, details: Optional[dict] = None):
        details = details or {}
        details["service"] = service_name
        super().__init__(message, "AZURE_SERVICE_ERROR", details)


class AIAgentError(ApplicationError):
    """AI agent execution error"""
    
    def __init__(self, message: str, agent_name: str, details: Optional[dict] = None):
        details = details or {}
        details["agent"] = agent_name
        super().__init__(message, "AI_AGENT_ERROR", details)


class PaperGenerationError(ApplicationError):
    """Paper generation workflow error"""
    
    def __init__(self, message: str, step: str, details: Optional[dict] = None):
        details = details or {}
        details["step"] = step
        super().__init__(message, "PAPER_GENERATION_ERROR", details)
