from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ClassifyResponse(BaseModel):
    area: str = Field(..., description="Predicted category")
    subarea: Optional[str] = Field(None, description="Predicted subcategory")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence")
    mode: str = Field(..., description="System mode: learning or auto")
    suggestions: Optional[List[str]] = Field(default_factory=list, description="Alternative suggestions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "area": "Finanse",
                "subarea": "Faktury", 
                "confidence": 0.85,
                "mode": "auto",
                "suggestions": ["Sluzbowe", "Daily Business"],
                "metadata": {"processing_time": "0.12s", "model_version": "1.0"},
                "timestamp": "2025-08-24T12:00:00Z"
            }
        }

class FeedbackResponse(BaseModel):
    success: bool = Field(..., description="Whether feedback was processed")
    message: str = Field(..., description="Response message")
    model_updated: bool = Field(False, description="Whether the model was retrained")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Feedback received and model updated",
                "model_updated": True
            }
        }