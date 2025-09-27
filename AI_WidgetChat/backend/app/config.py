import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./database/ai_widget_chat.db"
    
    # Google Cloud / VertexAI
    google_cloud_project: Optional[str] = None
    google_application_credentials: Optional[str] = None
    vertex_ai_location: str = "us-central1"
    
    # External APIs
    openweather_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    news_api_key: Optional[str] = None
    
    # Application Settings
    secret_key: Optional[str] = None
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:4200", "http://127.0.0.1:4200"]
    
    # Redis (optional)
    redis_url: str = "redis://localhost:6379/0"
    
    # Widget Settings
    widget_cache_ttl: int = 300  # 5 minutes
    max_widgets_per_response: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""  # No prefix, use exact environment variable names
    
    def validate_required_settings(self) -> None:
        """Validate that required environment variables are set."""
        required_vars = [
            "openweather_api_key",
            "alpha_vantage_api_key", 
            "news_api_key",
            "secret_key"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(self, var):
                missing_vars.append(var.upper())
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


# Global settings instance
settings = Settings()

# Validate required settings on startup
try:
    settings.validate_required_settings()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please set the required environment variables in your .env file or environment.")
