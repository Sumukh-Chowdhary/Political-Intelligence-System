from fastapi import APIRouter
from api.services.ml_service import ml_service

router = APIRouter(prefix="/api/v1", tags=["health"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": ml_service.is_loaded,
        "features": ml_service.feature_count
    }

@router.get("/info")
def get_info():
    return {
        "system": "Political Intelligence System",
        "api_version": "1.0.0",
        "model": "PyTorch Neural Network",
        "features": ml_service.feature_count,
        "device": "cpu"
    }