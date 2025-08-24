from fastapi import APIRouter, Depends
from dependencies import get_document_service
from core.document_service import DocumentService

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "message": "Document Classifier API is running",
        "version": "1.0.0"
    }

@router.get("/ready")
async def readiness_check(
    service: DocumentService = Depends(get_document_service)
):
    """Readiness check - is application ready to serve traffic"""
    try:
        # Check if service can respond
        mode = service.get_mode()
        can_predict = service.classifier.can_predict()
        
        return {
            "status": "ready",
            "mode": mode,
            "can_predict": can_predict,
            "database": "connected"  # TODO: add real DB check
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "error": str(e)
        }

@router.get("/live")
async def liveness_check():
    """Liveness check - is application alive"""
    return {"status": "alive"}