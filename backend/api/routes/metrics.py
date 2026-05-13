from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["metrics"])

class MetricsResponse(BaseModel):
    accuracy: float
    precision_winner: float
    recall_winner: float
    f1_score: float

@router.get("/metrics", response_model=MetricsResponse)
def get_metrics():
    return MetricsResponse(
        accuracy=0.9159,
        precision_winner=0.86,
        recall_winner=0.87,
        f1_score=0.86
    )