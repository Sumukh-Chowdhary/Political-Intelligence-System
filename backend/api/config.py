import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# backend/ is the root - two levels up from api/config.py
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    # ── Database ────────────────────────────────────────────────────────────
    PG_URI: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:sumukh04@localhost:5432/political_intelligence",
    )

    # ── ML Model artifacts ──────────────────────────────────────────────────
    MODEL_PATH   = BASE_DIR / "models" / "phase1_base_model.pth"
    SCALER_PATH  = BASE_DIR / "models" / "feature_scaler.joblib"
    FEATURES_PATH = BASE_DIR / "models" / "feature_columns.joblib"

    # ── CSV data ────────────────────────────────────────────────────────────
    DATA_DIR = BASE_DIR / "data" / "election_data"

    HOUSE_CSV        = DATA_DIR / "house_results_cleaned.csv"
    CENSUS_CSV       = DATA_DIR / "census_2024_435_cleaned.csv"
    PVI_CSV          = DATA_DIR / "state_pvi_cleaned.csv"
    PRESIDENTIAL_CSV = DATA_DIR / "presidential_results_cleaned.csv"
    HISTORY_CSV      = DATA_DIR / "district_history_cleaned.csv"

    # ── CORS ────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]