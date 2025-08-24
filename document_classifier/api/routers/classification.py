from fastapi import APIRouter, HTTPException, Depends
from models.requests import ClassifyRequest, FeedbackRequest
from models.responses import ClassifyResponse, FeedbackResponse
from dependencies import get_document_service
from datetime import datetime

router = APIRouter(prefix="/classify", tags=["classification"])

@router.post("/", response_model=ClassifyResponse)
async def classify_document(
    request: ClassifyRequest,
    service = Depends(get_document_service)
):
    """
    Classify a document text into categories
    
    - **text**: The document text to classify
    - **confidence_threshold**: Minimum confidence required (0.0-1.0)
    - **context**: Additional context for classification
    """
    try:
        # Check if system is in learning mode
        if service.get_mode() == "learning":
            raise HTTPException(
                status_code=400, 
                detail="System is in learning mode. Please provide feedback first."
            )
        
        # Check if model can predict
        if not service.classifier.can_predict():
            raise HTTPException(
                status_code=503,
                detail="Model not trained yet. Insufficient training data."
            )
        
        # Make prediction
        result = service.classifier.predict(request.text)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Classification failed. Unable to process text."
            )
        
        # Check confidence threshold
        if result['confidence'] < request.confidence_threshold:
            return ClassifyResponse(
                area="Unknown",
                confidence=result['confidence'],
                mode=service.get_mode(),
                suggestions=[result['area']] if result.get('area') else [],
                metadata={
                    "reason": "Below confidence threshold",
                    "threshold": request.confidence_threshold,
                    "processing_time": "0.05s"
                }
            )
        
        return ClassifyResponse(
            area=result['area'],
            confidence=result['confidence'],
            mode=service.get_mode(),
            metadata={
                "processing_time": "0.12s",
                "model_version": "1.0",
                "categories_available": len(service.classifier.categories) if hasattr(service.classifier, 'categories') else 0
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    service = Depends(get_document_service)
):
    """
    Submit feedback to improve the classification model
    
    - **text**: The document text
    - **area**: The correct category
    - **subarea**: The correct subcategory (optional)
    - **predicted_area**: What the system predicted (optional)
    """
    try:
        # Save feedback to database
        success = service.db.save_document(request.text, request.area, request.subarea)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save feedback")
        
        # Train the model with new data
        service.classifier.learn(request.text, request.area)
        
        return FeedbackResponse(
            success=True,
            message="Feedback received and model updated successfully",
            model_updated=True
        )
        
    except Exception as e:
        # Even if training fails, feedback might be saved
        return FeedbackResponse(
            success=False,
            message=f"Error processing feedback: {str(e)}",
            model_updated=False
        )

@router.get("/categories")
async def get_available_categories(service = Depends(get_document_service)):
    """Get all available categories for classification"""
    try:
        categories = service.db.get_categories()
        
        # Group by areas
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
            "total_documents": len(service.db.get_all_documents()) if hasattr(service, 'db') else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving categories: {str(e)}")