# core/document_service.py
from .database_pg import DatabaseManager
from .classifier import ClassificationEngine

class DocumentService:
    def __init__(self):
        self.db = DatabaseManager()
        self.classifier = ClassificationEngine()
        self.mode = "learning"  # learning lub auto
        
    def get_mode(self):
        """Zwraca aktualny tryb"""
        return self.mode
    
    def set_mode(self, mode):
        """Ustawia tryb: learning lub auto"""
        if mode in ["learning", "auto"]:
            self.mode = mode
            return True
        return False