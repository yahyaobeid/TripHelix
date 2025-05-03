"""
Configuration module for the TripHelix application.
This module defines all the configuration settings needed for the application,
including API settings, database connections, and AI service configurations.
"""

from pydantic_settings import BaseSettings
from typing import Optional

class AIConfig(BaseSettings):
    """
    Configuration class for AI services and application settings.
    This class uses Pydantic's BaseSettings to handle environment variables and default values.
    """
    
    # API Settings
    API_V1_STR: str = "/api/v1"  # Base path for API version 1
    PROJECT_NAME: str = "TripHelix"  # Name of the project

    # Database Settings
    POSTGRES_SERVER: str = "localhost"  # PostgreSQL server host
    POSTGRES_USER: str = "postgres"     # PostgreSQL username
    POSTGRES_PASSWORD: str = "postgres" # PostgreSQL password
    POSTGRES_DB: str = "triphelix"      # PostgreSQL database name

    # Redis Settings
    REDIS_HOST: str = "localhost"  # Redis server host
    REDIS_PORT: str = "6379"       # Redis server port

    # AI Settings
    OPENAI_API_KEY: str = "your_openai_api_key"  # OpenAI API key
    OPENAI_MODEL: str = "gpt-4o"                 # OpenAI model to use
    OPENAI_TEMPERATURE: float = 0.7              # Temperature for AI responses (0.0 to 1.0)
    OPENAI_MAX_TOKENS: int = 2000                # Maximum tokens in AI responses
    LANGCHAIN_API_KEY: str = "your_langchain_api_key"  # LangChain API key

    # Security Settings
    SECRET_KEY: str = "your_secret_key"          # Secret key for JWT tokens
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30        # JWT token expiration time in minutes
    
    # Pydantic model configuration
    model_config = {
        "env_file": ".env",  # Load environment variables from .env file
        "case_sensitive": True  # Environment variable names are case-sensitive
    }

# Create a global config instance
ai_config = AIConfig() 