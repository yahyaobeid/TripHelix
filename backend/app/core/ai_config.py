from pydantic_settings import BaseSettings
from typing import Optional

class AIConfig(BaseSettings):
    """Configuration for AI services and application settings"""
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TripHelix"

    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "triphelix"

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"

    # AI Settings
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000
    LANGCHAIN_API_KEY: str = "your_langchain_api_key"

    # Security
    SECRET_KEY: str = "your_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow"
    }

# Create a global config instance
ai_config = AIConfig() 