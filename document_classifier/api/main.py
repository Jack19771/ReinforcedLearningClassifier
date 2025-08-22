# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Dodaj ścieżkę do core
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.document_service import DocumentService

# Pydantic models
class ClassifyRequest(BaseModel):
    text: str

class ClassifyResponse(BaseModel):
    area: str
    confidence: float
    mode: str

class FeedbackRequest(BaseModel):
    text: str
    area: str
    subarea: Optional[str] = None

class StatsResponse(BaseModel):
    total_documents: int
    total_areas: int
    can_predict: bool
    mode: str
    categories: list

# FastAPI app
app = FastAPI(
    title="Document Classifier API",
    description="AI-powered document classification system",
    version="1.0.0"
)

# Global service instance
service = DocumentService()

@app.get("/")
def read_root():
    return {"message": "Document Classifier API", "version": "1.0.0"}

@app.post("/classify", response_model=ClassifyResponse)
def classify_document(request: ClassifyRequest):
    """Klasyfikuj dokument"""
    
    if service.get_mode() == "learning":
        raise HTTPException(status_code=400, detail="System is in learning mode")
    
    if not service.classifier.can_predict():
        raise HTTPException(status_code=400, detail="Model not trained yet")
    
    result = service.classifier.predict(request.text)
    
    if not result:
        raise HTTPException(status_code=400, detail="Unable to classify")
    
    return ClassifyResponse(
        area=result['area'],
        confidence=result['confidence'], 
        mode=service.get_mode()
    )

@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    """Wyślij feedback i naucz model"""
    
    # Zapisz do bazy
    service.db.save_document(request.text, request.area, request.subarea)
    
    # Naucz model
    service.classifier.learn(request.text, request.area)
    
    return {"message": "Feedback received and model updated"}

@app.get("/stats", response_model=StatsResponse)
def get_stats():
    """Pobierz statystyki systemu"""
    
    categories = service.db.get_categories()
    total_docs = len(service.db.get_all_documents())
    unique_areas = len(set(cat[0] for cat in categories))
    
    return StatsResponse(
        total_documents=total_docs,
        total_areas=unique_areas,
        can_predict=service.classifier.can_predict(),
        mode=service.get_mode(),
        categories=[{"area": cat[0], "subarea": cat[1]} for cat in categories]
    )

@app.post("/mode/{new_mode}")
def change_mode(new_mode: str):
    """Zmień tryb pracy"""
    
    if new_mode not in ["learning", "auto"]:
        raise HTTPException(status_code=400, detail="Mode must be 'learning' or 'auto'")
    
    if new_mode == "auto" and not service.classifier.can_predict():
        raise HTTPException(status_code=400, detail="Cannot switch to auto mode - model not ready")
    
    service.set_mode(new_mode)
    return {"message": f"Mode changed to {new_mode}"}

@app.post("/load-starter-data")
def load_starter_data_endpoint():
    """Załaduj przykładowe dane"""
    from core.starter_data import load_starter_data
    
    load_starter_data(service.db, service.classifier)
    service.set_mode("auto")
    
    return {"message": "Starter data loaded successfully"}


# api/main.py - dodaj na końcu przed if __name__

from pydantic import BaseModel
from typing import Optional, Dict, Any

# Universal Models
class UniversalClassifyRequest(BaseModel):
    text: str
    context: Optional[Dict[str, Any]] = {}  # Dodatkowy kontekst
    system_id: Optional[str] = None         # ID systemu wywołującego
    confidence_threshold: Optional[float] = 0.7

class UniversalClassifyResponse(BaseModel):
    area: str
    subarea: Optional[str]
    confidence: float
    system_id: Optional[str]
    metadata: Dict[str, Any]
    timestamp: str
    suggestions: Optional[list] = []        # Alternatywne klasyfikacje

class UniversalFeedbackRequest(BaseModel):
    text: str
    correct_area: str
    correct_subarea: Optional[str] = None
    predicted_area: Optional[str] = None    # Co system przewidział
    system_id: Optional[str] = None
    user_id: Optional[str] = None

class SystemConfigRequest(BaseModel):
    system_id: str
    categories_mapping: Optional[Dict[str, str]] = {}  # Mapowanie kategorii
    confidence_threshold: Optional[float] = 0.7
    auto_learn: Optional[bool] = True

# Universal Endpoints
@app.post("/v1/classify", response_model=UniversalClassifyResponse)
def universal_classify(request: UniversalClassifyRequest):
    """Universal document classification endpoint"""
    
    if not service.classifier.can_predict():
        raise HTTPException(status_code=503, detail="Model not ready - insufficient training data")
    
    result = service.classifier.predict(request.text)
    
    if not result:
        raise HTTPException(status_code=500, detail="Classification failed")
    
    # Check confidence threshold
    if result['confidence'] < request.confidence_threshold:
        suggestions = get_alternative_classifications(request.text)
    else:
        suggestions = []
    
    return UniversalClassifyResponse(
        area=result['area'],
        subarea=None,  # TODO: extend classifier for subareas
        confidence=result['confidence'],
        system_id=request.system_id,
        metadata={
            "processing_time": "0.12s",  # TODO: measure real time
            "model_version": "1.0",
            "categories_available": list(service.classifier.categories)
        },
        timestamp=datetime.now().isoformat(),
        suggestions=suggestions
    )

@app.post("/v1/feedback")
def universal_feedback(request: UniversalFeedbackRequest):
    """Universal feedback endpoint for model improvement"""
    
    # Save to database
    service.db.save_document(request.text, request.correct_area, request.correct_subarea)
    
    # Train model
    service.classifier.learn(request.text, request.correct_area)
    
    # Log feedback for analytics
    log_feedback(request)
    
    return {
        "success": True,
        "message": "Feedback received and model updated",
        "system_id": request.system_id
    }

@app.get("/v1/categories")
def get_available_categories():
    """Get all available categories for dropdown lists"""
    
    categories = service.db.get_categories()
    
    areas = {}
    for area, subarea in categories:
        if area not in areas:
            areas[area] = []
        if subarea and subarea not in areas[area]:
            areas[area].append(subarea)
    
    return {
        "areas": list(areas.keys()),
        "categories": areas,
        "total_areas": len(areas),
        "total_documents": len(service.db.get_all_documents())
    }

@app.post("/v1/config/system")
def configure_system(config: SystemConfigRequest):
    """Configure system-specific settings"""
    
    # TODO: Save system config to database
    # For now, just return success
    
    return {
        "success": True,
        "system_id": config.system_id,
        "message": f"Configuration saved for {config.system_id}"
    }

@app.get("/v1/health")
def health_check():
    """Health check endpoint for monitoring"""
    
    return {
        "status": "healthy",
        "model_ready": service.classifier.can_predict(),
        "categories_count": len(service.classifier.categories),
        "documents_count": len(service.db.get_all_documents()),
        "mode": service.get_mode(),
        "version": "1.0.0",
        "uptime": "TODO",  # TODO: track uptime
        "timestamp": datetime.now().isoformat()
    }

@app.get("/v1/batch/classify")
async def batch_classify():
    """Batch classification endpoint for processing multiple documents"""
    # TODO: Implement batch processing
    return {"message": "Batch processing endpoint - coming soon"}

# Helper functions
def get_alternative_classifications(text: str, limit: int = 3):
    """Get alternative classification suggestions"""
    # TODO: Implement proper alternative suggestions
    return []

def log_feedback(feedback: UniversalFeedbackRequest):
    """Log feedback for analytics"""
    # TODO: Implement proper logging
    pass

from datetime import datetime



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)