"""
FastAPI Backend for Political Intelligence System
Serves model predictions and metrics to React frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from pydantic import BaseModel
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Political Intelligence API",
    description="ML model serving and election data API",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Load Model and Data
# ============================================================================

model = None
house_data = None
census_data = None
state_pvi_data = None

def load_resources():
    """Load model and datasets on startup"""
    global model, house_data, census_data, state_pvi_data
    
    try:
        # Load model
        model_path = Path(__file__).parent.parent / 'models' / 'xgb_gpu_pipeline.joblib'
        model = joblib.load(model_path)
        logger.info(f"Model loaded from {model_path}")
        
        # Load datasets
        data_dir = Path(__file__).parent.parent / 'data' / 'election_data'
        house_data = pd.read_csv(data_dir / 'house_results_cleaned.csv')
        census_data = pd.read_csv(data_dir / 'census_2024_435_cleaned.csv')
        state_pvi_data = pd.read_csv(data_dir / 'state_pvi_cleaned.csv')
        
        logger.info("All datasets loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load resources: {e}")
        raise

# ============================================================================
# Request/Response Models
# ============================================================================

class PredictionRequest(BaseModel):
    """Request model for predictions"""
    party: str
    candidate_votes: int
    total_votes: int
    district_id: int
    state: str
    year: int
    census_data: dict = {}

class PredictionResponse(BaseModel):
    """Response model for predictions"""
    prediction: int
    probability: float
    is_winner: bool
    confidence: float

class MetricsResponse(BaseModel):
    """Model performance metrics"""
    accuracy: float
    precision_winner: float
    recall_winner: float
    f1_score: float
    best_log_loss: float

# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Load resources on startup"""
    load_resources()

@app.get("/health")
def health_check():
    """Check if API is running"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "data_loaded": house_data is not None
    }

@app.get("/api/v1/info")
def get_info():
    """Get system information"""
    return {
        "system": "Political Intelligence System",
        "api_version": "1.0.0",
        "model": "XGBoost (GPU-enabled)",
        "features": 244,
        "training_samples": 14781,
        "validation_accuracy": 0.9159
    }

# ============================================================================
# Prediction Endpoint
# ============================================================================

@app.post("/api/v1/predict", response_model=PredictionResponse)
def make_prediction(request: PredictionRequest):
    """
    Make election outcome prediction
    
    Args:
        request: PredictionRequest with candidate and district info
    
    Returns:
        PredictionResponse with prediction and confidence
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Prepare feature vector (simplified - in production, prepare full 244 features)
        X = pd.DataFrame([{
            'party': request.party,
            'candidate_votes': request.candidate_votes,
            'total_votes': request.total_votes,
            **request.census_data
        }])
        
        # Make prediction
        prediction = model.predict(X)[0]
        probability = model.predict_proba(X)[0]
        
        return PredictionResponse(
            prediction=int(prediction),
            probability=float(probability[1]),
            is_winner=bool(prediction),
            confidence=float(max(probability))
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Metrics Endpoint
# ============================================================================

@app.get("/api/v1/metrics", response_model=MetricsResponse)
def get_model_metrics():
    """Get model performance metrics"""
    return MetricsResponse(
        accuracy=0.9159,
        precision_winner=0.86,
        recall_winner=0.87,
        f1_score=0.86,
        best_log_loss=0.1850
    )

# ============================================================================
# Data Endpoints
# ============================================================================

@app.get("/api/v1/house-results")
def get_house_results(state: str = None, year: int = None, limit: int = 100):
    """Get house election results"""
    if house_data is None:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    data = house_data.copy()
    
    if state:
        data = data[data['state'] == state]
    
    if year:
        data = data[data['year'] == year]
    
    return {
        "data": data.head(limit).to_dict(orient='records'),
        "total_rows": len(data),
        "returned": min(limit, len(data))
    }

@app.get("/api/v1/census-data")
def get_census_data(limit: int = 100):
    """Get census demographics"""
    if census_data is None:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    return {
        "data": census_data.head(limit).to_dict(orient='records'),
        "total_rows": len(census_data),
        "returned": min(limit, len(census_data))
    }

@app.get("/api/v1/state-pvi")
def get_state_pvi():
    """Get state PVI (Partisan Voting Index)"""
    if state_pvi_data is None:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    return {
        "data": state_pvi_data.to_dict(orient='records'),
        "total_rows": len(state_pvi_data)
    }

# ============================================================================
# Statistics Endpoints
# ============================================================================

@app.get("/api/v1/statistics")
def get_statistics():
    """Get overall statistics"""
    if house_data is None:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    return {
        "total_elections": len(house_data),
        "districts": len(census_data) if census_data is not None else 0,
        "states": len(state_pvi_data) if state_pvi_data is not None else 0,
        "years": f"{house_data['year'].min()}-{house_data['year'].max()}",
        "parties": house_data['party_clean'].unique().tolist() if 'party_clean' in house_data.columns else [],
        "elections_by_year": house_data.groupby('year').size().to_dict()
    }

# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
def root():
    """API documentation"""
    return {
        "message": "Political Intelligence System API",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "info": "/api/v1/info",
            "predict": "POST /api/v1/predict",
            "metrics": "/api/v1/metrics",
            "statistics": "/api/v1/statistics",
            "data": {
                "house_results": "/api/v1/house-results",
                "census": "/api/v1/census-data",
                "state_pvi": "/api/v1/state-pvi"
            }
        }
    }

# ============================================================================
# Run with: uvicorn api/server:app --reload --port 8000
# ============================================================================
