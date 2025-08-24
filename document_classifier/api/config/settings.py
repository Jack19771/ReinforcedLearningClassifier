from pydantic_settings import BaseSettings  # <-- ZMIANA
from typing import List

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://app_user:app_password@postgres-cluster-rw:5432/document_classifier"
    database_pool_size: int = 10
    
    # Application
    app_title: str = "Document Classifier API"
    app_version: str = "1.0.0"
    app_description: str = "AI-powered document classification system"
    
    # API Configuration  
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["*"]
    
    # ML Model
    model_confidence_threshold: float = 0.7
    model_learning_mode: str = "learning"  # learning | auto
    
    # Logging
    log_level: str = "INFO"
    
    # Environment  
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        env_prefix = "API_"
        case_sensitive = False

# Singleton instance
settings = Settings()