# Political Intelligence System - Dashboard Setup

## 🚀 Quick Start

### Option 1: Streamlit Dashboard (Recommended)

The simplest way to run the dashboard.

#### Prerequisites
```bash
pip install streamlit plotly pandas numpy joblib
```

Or install from requirements:
```bash
pip install -r requirements.txt
```

#### Run the Dashboard
```bash
cd c:\Users\B\Docs\Projects\Political-Intelligence-System
streamlit run api/dashboard.py
```

The dashboard will open at `http://localhost:8501`

#### Dashboard Features
- **Dashboard Page**: Overview metrics, election trends, party distribution
- **Model Performance**: Accuracy, precision, recall, confusion matrix, feature importance
- **Predictions**: Interface to make predictions (expandable feature)
- **Data Explorer**: Browse raw data from house results, census, and state PVI

---

### Option 2: React + API Backend (Advanced)

For a more sophisticated frontend with real-time predictions.

#### Step 1: Create React Frontend

```bash
# Create React app in project root
npx create-react-app frontend
cd frontend
npm install axios react-router-dom plotly.js react-plotly.js
```

#### Step 2: Create FastAPI Backend

```bash
pip install fastapi uvicorn python-multipart
```

Create `api/server.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import numpy as np

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
model = joblib.load('models/xgb_gpu_pipeline.joblib')

@app.get("/api/health")
def health():
    return {"status": "healthy"}

@app.post("/api/predict")
def predict(data: dict):
    # Prepare data for model
    X = pd.DataFrame([data])
    prediction = model.predict(X)
    probability = model.predict_proba(X)
    
    return {
        "prediction": int(prediction[0]),
        "probability": float(probability[0][1]),
        "is_winner": bool(prediction[0])
    }

@app.get("/api/model/metrics")
def get_metrics():
    return {
        "accuracy": 0.9159,
        "precision": 0.86,
        "recall": 0.87,
        "best_score": 0.1850
    }
```

Run backend:
```bash
uvicorn api.server:app --reload --port 8000
```

#### Step 3: Run React Frontend

```bash
cd frontend
npm start
```

Runs on `http://localhost:3000`

---

## 📊 Dashboard Pages

### 1. Dashboard
- Election metrics and trends
- Party distribution
- Top states by election count
- Historical data visualization

### 2. Model Performance
- Accuracy: 91.59%
- Precision & Recall by class
- Confusion matrix heatmap
- Feature importance chart
- Model specifications

### 3. Predictions
- Input form for candidate data
- Real-time prediction results
- Confidence scores
- Historical comparison

### 4. Data Explorer
- Browse house election results
- Filter by year and state
- Census demographics lookup
- State PVI reference

---

## 🔧 Configuration

### Environment Variables
Create a `.env` file in `api/` directory:
```
STREAMLIT_SERVER_PORT=8501
STREAMLIT_LOGGER_LEVEL=info
```

---

## 📦 Dependencies

Core:
- `streamlit` - Web framework for dashboards
- `plotly` - Interactive visualizations
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `joblib` - Model serialization
- `xgboost` - Gradient boosting model

Optional (for React):
- `fastapi` - Backend API
- `uvicorn` - ASGI server
- `react` - Frontend framework
- `plotly.js` - JavaScript visualizations

---

## 🚨 Troubleshooting

**Model not loading:**
- Ensure `models/xgb_gpu_pipeline.joblib` exists
- Run `baseline_model.ipynb` cells 1-8 to train and save

**Streamlit not starting:**
```bash
pip install --upgrade streamlit
```

**Data files not found:**
- Ensure CSV files exist in `data/election_data/`

---

## 📈 Next Steps

1. ✅ Run Streamlit dashboard and explore
2. ✅ Test model predictions in "Predictions" tab
3. Optional: Deploy FastAPI backend to cloud
4. Optional: Deploy React frontend to Vercel/Netlify
5. Optional: Add Neo4j integration for graph queries

---

## 📝 Usage Examples

### Run Streamlit
```bash
streamlit run api/dashboard.py
```

### Run with custom config
```bash
streamlit run api/dashboard.py --logger.level=debug
```

### Run Streamlit + API Backend
```bash
# Terminal 1: Start API
uvicorn api.server:app --reload

# Terminal 2: Start Streamlit  
streamlit run api/dashboard.py
```

---

Built with ❤️ for Political Intelligence System
