from functools import lru_cache
from config.settings import Settings
import sys
import os
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

@lru_cache()
def get_settings() -> Settings:
    return Settings()

@lru_cache()
def get_document_service():
    """Environment-aware document service"""
    settings = get_settings()
    
    try:
        # Try to import real service (works in Kubernetes)
        from core.document_service import DocumentService
        return DocumentService()
    except Exception as e:
        print(f"⚠️  Real service failed ({e}), using mock for local development")
        return MockDocumentService()

# Mock service for local development
class MockDocumentService:
    """Mock service when database is not available"""
    def __init__(self):
        self.classifier = MockClassifier()
    
    def get_mode(self):
        return "learning"

class MockClassifier:
    """Mock classifier for local development"""
    def can_predict(self):
        return False  # No real model in local development
    
    @property
    def categories(self):
        return set()