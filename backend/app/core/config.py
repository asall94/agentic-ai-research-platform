from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Advanced Agentic Research Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # API Keys
    OPENAI_API_KEY: str
    TAVILY_API_KEY: str = ""
    
    # Model Defaults
    DEFAULT_DRAFT_MODEL: str = "openai:gpt-4o"
    DEFAULT_REFLECTION_MODEL: str = "openai:gpt-4o-mini"
    DEFAULT_RESEARCH_MODEL: str = "openai:gpt-4o"
    DEFAULT_WRITER_MODEL: str = "openai:gpt-4o"
    DEFAULT_EDITOR_MODEL: str = "openai:gpt-4o"
    DEFAULT_PLANNER_MODEL: str = "openai:gpt-4o-mini"
    
    # Temperature
    DEFAULT_TEMPERATURE: float = 0.7
    CREATIVE_TEMPERATURE: float = 1.0
    PRECISE_TEMPERATURE: float = 0.3
    
    # Tools
    ENABLE_ARXIV: bool = True
    ENABLE_TAVILY: bool = True
    ENABLE_WIKIPEDIA: bool = True
    MAX_SEARCH_RESULTS: int = 5
    
    # Workflow
    MAX_WORKFLOW_STEPS: int = 4
    MAX_TOOL_TURNS: int = 6
    REQUEST_TIMEOUT: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
