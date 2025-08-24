from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="Text to classify")
    confidence_threshold: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="Minimum confidence threshold")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Invoice from ABC Company for office supplies totaling $1,247.89",
                "confidence_threshold": 0.7,
                "context": {"user_id": "123", "source": "email"}
            }
        }

class FeedbackRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    area: str = Field(..., min_length=1, max_length=100)
    subarea: Optional[str] = Field(None, max_length=100)
    predicted_area: Optional[str] = Field(None, description="What the system predicted")
    user_id: Optional[str] = Field(None, description="User who provided feedback")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Meeting notes from quarterly planning session",
                "area": "Sluzbowe", 
                "subarea": "Spotkania",
                "predicted_area": "Daily Business",
                "user_id": "user_123"
            }
        }