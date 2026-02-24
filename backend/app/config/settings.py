from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # FastAPI
    APP_NAME: str = "Interview Question Paper Generator"
    DEBUG: bool = False
    
    # Azure Service Bus
    AZURE_SERVICE_BUS_CONNECTION_STRING: str
    SERVICE_BUS_QUEUE_NAME: str = "paper-generation-queue"
    
    # Azure Cosmos DB
    COSMOS_DB_CONNECTION_STRING: str
    COSMOS_DB_DATABASE_NAME: str = "interviewdb"
    COSMOS_DB_CONTAINER_NAME: str = "users"
    
    # Azure Blob Storage
    AZURE_STORAGE_ACCOUNT_NAME: str
    AZURE_STORAGE_ACCOUNT_KEY: str
    BLOB_CONTAINER_NAME: str = "questions"
    
    # OpenAI / Claude Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_PROVIDER: str = "anthropic"  # "openai" or "anthropic"
    AI_MODEL: str = "claude-3-sonnet-20240229"
    
    # Retry Configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    RETRY_BACKOFF: float = 2.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
