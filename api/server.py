from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Political Intelligence API",
    description="ML model serving and election data API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ElectionPredictor(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.network(x)

model = None
scaler = None
feature_columns = None
house_data = None
census_data = None
state_pvi_data = None

def load_resources():
    global model, scaler, feature_columns, house_data, census_data, state_pvi_data
    
    try:
        models_dir = Path(__file__).parent.parent / 'models'
        
        model_path = models_dir / 'phase1_base_model.pth'
        scaler_path = models_dir / 'feature_scaler.joblib'
        features_path = models_dir / 'feature_columns.joblib'
        
        scaler = joblib.load(scaler_path)
        feature_columns = joblib.load(features_path)
        
        input_dim = len(feature_columns)
        model = ElectionPredictor(input_dim)
        model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
        model.eval()
        
        logger.info(f"Model loaded from {model_path}")
        logger.info(f"Input dimension: {input_dim}")
        
        data_dir = Path(__file__).parent.parent / 'data' / 'election_data'
        house_data = pd.read_csv(data_dir / 'house_results_cleaned.csv', low_memory=False)
        census_data = pd.read_csv(data_dir / 'census_2024_435_cleaned.csv')
        state_pvi_data = pd.read_csv(data_dir / 'state_pvi_cleaned.csv')
        
        logger.info("All datasets loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load resources: {e}")
        raise

class PredictionRequest(BaseModel):
    features: Dict[str, Any]

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    is_winner: bool
    confidence: float
    predicted_party: str

class MetricsResponse(BaseModel):
    accuracy: float
    precision_winner: float
    recall_winner: float
    f1_score: float

class DistrictPredictionResponse(BaseModel):
    district_id: str
    state: str
    year: int
    predicted_winner: str
    win_probability: float
    confidence: float
    features_used: int

class PredictionsListResponse(BaseModel):
    data: List[Dict[str, Any]]
    total_rows: int

class StatePredictionsResponse(BaseModel):
    state: str
    year: int
    data: List[Dict[str, Any]]
    total_districts: int

class PredictionsSummaryResponse(BaseModel):
    year: int
    total_districts_processed: int
    democrat_projections: int
    republican_projections: int
    democrat_percentage: float
    republican_percentage: float

@app.on_event("startup")
async def startup_event():
    load_resources()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "data_loaded": house_data is not None
    }

@app.get("/api/v1/info")
def get_info():
    return {
        "system": "Political Intelligence System",
        "api_version": "1.0.0",
        "model": "PyTorch Neural Network",
        "features": len(feature_columns) if feature_columns is not None else 0,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }

@app.post("/api/v1/predict", response_model=PredictionResponse)
def make_prediction(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        feature_df = pd.DataFrame([request.features])
        
        for col in feature_columns:
            if col not in feature_df.columns:
                feature_df[col] = 0
        
        feature_df = feature_df[feature_columns]
        feature_df = feature_df.fillna(0).astype(np.float32)
        
        X_scaled = scaler.transform(feature_df)
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
        
        with torch.no_grad():
            probability = model(X_tensor).numpy().flatten()[0]
        
        prediction = 1 if probability > 0.5 else 0
        predicted_party = "Republican" if prediction == 1 else "Democrat"
        
        return PredictionResponse(
            prediction=int(prediction),
            probability=float(probability),
            is_winner=bool(prediction),
            confidence=float(probability if prediction == 1 else 1 - probability),
            predicted_party=predicted_party
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/metrics", response_model=MetricsResponse)
def get_model_metrics():
    return MetricsResponse(
        accuracy=0.99,
        precision_winner=0.86,
        recall_winner=0.87,
        f1_score=0.86
    )

@app.get("/api/v1/house-results")
def get_house_results(
    state: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    limit: int = Query(100, le=1000)
):
    if house_data is None:
        raise HTTPException(status_code=503, detail="Data not loaded")

    data = house_data.copy()

    if state:
        data = data[data['state'] == state]

    if year:
        data = data[data['year'] == year]

    data = data.head(limit)
    data = data.replace([np.inf, -np.inf], 0).fillna("")

    return {
        "data": data.to_dict(orient='records'),
        "total_rows": int(len(house_data)),
        "returned": int(len(data))
    }

@app.get("/api/v1/census-data")
def get_census_data(limit: int = Query(100, le=435)):
    if census_data is None:
        raise HTTPException(status_code=503, detail="Data not loaded")

    data = census_data.head(limit).copy()
    data = data.replace([np.inf, -np.inf], 0).replace({np.nan: None})

    records = []
    for row in data.to_dict(orient="records"):
        cleaned_row = {}
        for key, value in row.items():
            if pd.isna(value):
                cleaned_row[key] = None
            elif isinstance(value, (np.integer, np.int64)):
                cleaned_row[key] = int(value)
            elif isinstance(value, (np.floating, np.float64)):
                cleaned_row[key] = float(value)
            else:
                cleaned_row[key] = value
        records.append(cleaned_row)

    return {
        "data": records,
        "total_rows": int(len(census_data)),
        "returned": int(len(records))
    }

@app.get("/api/v1/state-pvi")
def get_state_pvi():
    if state_pvi_data is None:
        raise HTTPException(status_code=503, detail="Data not loaded")

    data = state_pvi_data.copy()
    data = data.replace([np.inf, -np.inf], 0).replace({np.nan: None})

    records = []
    for row in data.to_dict(orient="records"):
        cleaned_row = {}
        for key, value in row.items():
            if pd.isna(value):
                cleaned_row[key] = None
            elif isinstance(value, (np.integer, np.int64)):
                cleaned_row[key] = int(value)
            elif isinstance(value, (np.floating, np.float64)):
                cleaned_row[key] = float(value)
            else:
                cleaned_row[key] = value
        records.append(cleaned_row)

    return {
        "data": records,
        "total_rows": int(len(records))
    }

@app.get("/api/v1/predictions", response_model=PredictionsListResponse)
def get_all_predictions(
    state: Optional[str] = Query(None),
    year: int = Query(2024),
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=200)
):
    if house_data is None or model is None:
        raise HTTPException(status_code=503, detail="Model or data not loaded")
    
    try:
        filtered_data = house_data[house_data['year'] == year].copy()
        
        if state:
            filtered_data = filtered_data[filtered_data['state'] == state]
        
        unique_districts = filtered_data.drop_duplicates(subset=['district_id'])
        
        total_districts = len(unique_districts)
        offset = (page - 1) * limit
        paginated_districts = unique_districts.iloc[offset:offset + limit]
        
        predictions_list = []
        
        for idx, row in paginated_districts.iterrows():
            try:
                feature_dict = {}
                for col in feature_columns:
                    if col in paginated_districts.columns:
                        val = row[col]
                        if pd.isna(val):
                            val = 0
                        feature_dict[col] = val
                    else:
                        feature_dict[col] = 0
                
                feature_df = pd.DataFrame([feature_dict])
                feature_df = feature_df[feature_columns].fillna(0).astype(np.float32)
                X_scaled = scaler.transform(feature_df)
                X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
                
                with torch.no_grad():
                    probability = model(X_tensor).numpy().flatten()[0]
                
                prediction = 1 if probability > 0.5 else 0
                predicted_party = "Republican" if prediction == 1 else "Democrat"
                
                predictions_list.append({
                    "district": str(row.get('district_id', 'Unknown')),
                    "state": str(row.get('state', 'Unknown')),
                    "year": year,
                    "predicted_winner": predicted_party,
                    "win_probability": float(probability),
                    "confidence": float(probability if prediction == 1 else 1 - probability)
                })
            except Exception as e:
                logger.warning(f"Skipping row {idx}: {e}")
                continue
        
        return {
            "data": predictions_list,
            "total_rows": total_districts,
            "page": page,
            "limit": limit,
            "total_pages": (total_districts + limit - 1) // limit
        }
    except Exception as e:
        logger.error(f"Predictions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/predictions/state/{state}")
def get_predictions_by_state(
    state: str,
    year: int = Query(2024)
):
    if house_data is None or model is None:
        raise HTTPException(status_code=503, detail="Model or data not loaded")
    
    try:
        state_data = house_data[
            (house_data['state'] == state) & 
            (house_data['year'] == year)
        ].drop_duplicates(subset=['district_id'])
        
        if state_data.empty:
            raise HTTPException(status_code=404, detail=f"No districts found for state {state}")
        
        predictions_list = []
        
        for idx, row in state_data.iterrows():
            try:
                feature_dict = {}
                for col in feature_columns:
                    if col in state_data.columns:
                        val = row[col]
                        if pd.isna(val):
                            val = 0
                        feature_dict[col] = val
                    else:
                        feature_dict[col] = 0
                
                feature_df = pd.DataFrame([feature_dict])
                feature_df = feature_df[feature_columns].fillna(0).astype(np.float32)
                X_scaled = scaler.transform(feature_df)
                X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
                
                with torch.no_grad():
                    probability = model(X_tensor).numpy().flatten()[0]
                
                prediction = 1 if probability > 0.5 else 0
                predicted_party = "Republican" if prediction == 1 else "Democrat"
                
                predictions_list.append({
                    "district": str(row.get('district_id', 'Unknown')),
                    "state": state,
                    "year": year,
                    "predicted_winner": predicted_party,
                    "win_probability": float(probability),
                    "confidence": float(probability if prediction == 1 else 1 - probability)
                })
            except Exception as e:
                logger.warning(f"Skipping row {idx}: {e}")
                continue
        
        return {
            "state": state,
            "year": year,
            "data": predictions_list,
            "total_districts": len(predictions_list)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Predictions error for state {state}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/predictions/summary")
def get_predictions_summary(year: int = Query(2024)):
    if house_data is None or model is None:
        raise HTTPException(status_code=503, detail="Model or data not loaded")
    
    try:
        year_data = house_data[house_data['year'] == year].drop_duplicates(subset=['district_id'])
        
        democrat_wins = 0
        republican_wins = 0
        total_processed = 0
        
        for idx, row in year_data.iterrows():
            try:
                feature_dict = {}
                for col in feature_columns:
                    if col in year_data.columns:
                        val = row[col]
                        if pd.isna(val):
                            val = 0
                        feature_dict[col] = val
                    else:
                        feature_dict[col] = 0
                
                feature_df = pd.DataFrame([feature_dict])
                feature_df = feature_df[feature_columns].fillna(0).astype(np.float32)
                X_scaled = scaler.transform(feature_df)
                X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
                
                with torch.no_grad():
                    probability = model(X_tensor).numpy().flatten()[0]
                
                prediction = 1 if probability > 0.5 else 0
                
                if prediction == 0:
                    democrat_wins += 1
                else:
                    republican_wins += 1
                
                total_processed += 1
            except Exception as e:
                logger.warning(f"Skipping row {idx}: {e}")
                continue
        
        return {
            "year": year,
            "total_districts_processed": total_processed,
            "democrat_projections": democrat_wins,
            "republican_projections": republican_wins,
            "democrat_percentage": round(democrat_wins / total_processed * 100, 2) if total_processed > 0 else 0,
            "republican_percentage": round(republican_wins / total_processed * 100, 2) if total_processed > 0 else 0
        }
    except Exception as e:
        logger.error(f"Summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/predictions/{district_id}", response_model=DistrictPredictionResponse)
def get_prediction_by_district(district_id: str, year: int = Query(2024)):
    if house_data is None or model is None:
        raise HTTPException(status_code=503, detail="Model or data not loaded")
    
    try:
        district_data = house_data[
            (house_data['district_id'] == district_id) & 
            (house_data['year'] == year)
        ]
        
        if district_data.empty:
            raise HTTPException(status_code=404, detail=f"District {district_id} not found for year {year}")
        
        row = district_data.iloc[0]
        
        feature_dict = {}
        for col in feature_columns:
            if col in district_data.columns:
                val = row[col]
                if pd.isna(val):
                    val = 0
                feature_dict[col] = val
            else:
                feature_dict[col] = 0
        
        feature_df = pd.DataFrame([feature_dict])
        feature_df = feature_df[feature_columns].fillna(0).astype(np.float32)
        X_scaled = scaler.transform(feature_df)
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
        
        with torch.no_grad():
            probability = model(X_tensor).numpy().flatten()[0]
        
        prediction = 1 if probability > 0.5 else 0
        predicted_party = "Republican" if prediction == 1 else "Democrat"
        
        return DistrictPredictionResponse(
            district_id=district_id,
            state=str(row.get('state', 'Unknown')),
            year=year,
            predicted_winner=predicted_party,
            win_probability=float(probability),
            confidence=float(probability if prediction == 1 else 1 - probability),
            features_used=len(feature_columns)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error for district {district_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/statistics")
def get_statistics():
    if house_data is None:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    return {
        "total_elections": int(len(house_data)),
        "districts": int(len(census_data)) if census_data is not None else 0,
        "states": int(len(state_pvi_data)) if state_pvi_data is not None else 0,
        "years": f"{int(house_data['year'].min())}-{int(house_data['year'].max())}",
        "unique_states": int(house_data['state'].nunique()),
        "unique_districts": int(house_data['district_id'].nunique())
    }

@app.get("/")
def root():
    return {
        "message": "Political Intelligence System API",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "info": "/api/v1/info",
            "predict": "POST /api/v1/predict",
            "metrics": "/api/v1/metrics",
            "statistics": "/api/v1/statistics",
            "predictions": {
                "all": "GET /api/v1/predictions",
                "by_district": "GET /api/v1/predictions/{district_id}"
            },
            "data": {
                "house_results": "GET /api/v1/house-results",
                "census": "GET /api/v1/census-data",
                "state_pvi": "GET /api/v1/state-pvi"
            }
        }
    }