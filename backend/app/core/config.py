# Import necessary components from pydantic_settings for configuration management
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings class that inherits from BaseSettings.
    This class handles all configuration variables and their validation.
    """
    
    # API Settings
    API_V1_STR: str = "/api/v1"  # Base path for API version 1
    PROJECT_NAME: str = "TripHelix"  # Project name for documentation and logging
    
    # Database Settings
    POSTGRES_SERVER: str = "localhost"  # PostgreSQL server hostname
    POSTGRES_USER: str = "postgres"  # PostgreSQL username
    POSTGRES_PASSWORD: str = "postgres"  # PostgreSQL password
    POSTGRES_DB: str = "triphelix"  # PostgreSQL database name
    SQLALCHEMY_DATABASE_URI: Optional[str] = None  # Will be constructed if not provided
    
    # Redis Settings
    REDIS_HOST: str = "localhost"  # Redis server hostname
    REDIS_PORT: int = 6379  # Redis server port
    
    # AI Settings
    OPENAI_API_KEY: Optional[str] = None  # OpenAI API key for GPT models
    LANGCHAIN_API_KEY: Optional[str] = None  # LangChain API key for additional features
    
    class Config:
        """
        Pydantic configuration class.
        Defines how settings are loaded and validated.
        """
        env_file = ".env"  # Load settings from .env file
        case_sensitive = True  # Environment variable names are case-sensitive

    def __init__(self, **kwargs):
        """
        Initialize settings and construct database URI if not provided.
        """
        super().__init__(**kwargs)
        if not self.SQLALCHEMY_DATABASE_URI:
            # Construct PostgreSQL connection string if not provided
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
            )

# Create a global settings instance
settings = Settings()
