import joblib
import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from api.config import Config
import logging

logger = logging.getLogger(__name__)


class ElectionPredictor(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, 64),        nn.BatchNorm1d(64),  nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(64, 32),         nn.BatchNorm1d(32),  nn.ReLU(), nn.Dropout(0.1),
            nn.Linear(32, 1),          nn.Sigmoid(),
        )

    def forward(self, x):
        return self.network(x)


class MLService:
    """Singleton that loads the PyTorch model once and serves predictions."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # only initialise attributes once
        if not hasattr(self, "_initialised"):
            self._model: ElectionPredictor | None = None
            self._scaler = None
            self._feature_columns: list | None = None
            self._initialised = True

    # ── Load ─────────────────────────────────────────────────────────────────

    def load(self) -> bool:
        try:
            self._scaler = joblib.load(Config.SCALER_PATH)
            self._feature_columns = joblib.load(Config.FEATURES_PATH)

            input_dim = len(self._feature_columns)
            self._model = ElectionPredictor(input_dim)
            self._model.load_state_dict(
                torch.load(Config.MODEL_PATH, map_location="cpu")
            )
            self._model.eval()

            logger.info(f"Model loaded — {input_dim} features")
            return True

        except FileNotFoundError as e:
            logger.warning(f"Model file not found ({e}) — running without ML model")
            return False
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            return False

    # ── Predict ──────────────────────────────────────────────────────────────

    def predict(self, features: dict) -> dict:
        if self._model is None:
            raise RuntimeError("Model not loaded — call ml_service.load() first")

        # ── Create dataframe from input ───────────────────────────────
        df = pd.DataFrame([features])

        # ── Add missing columns efficiently ───────────────────────────
        missing_cols = [
            col for col in self._feature_columns
            if col not in df.columns
        ]

        if missing_cols:
            missing_df = pd.DataFrame(
                0,
                index=df.index,
                columns=missing_cols
            )

            # Add all missing columns at once
            df = pd.concat([df, missing_df], axis=1)

        # ── Keep exact feature order expected by model ───────────────
        df = df[self._feature_columns]

        # ── Fill nulls + ensure float32 ──────────────────────────────
        df = df.fillna(0).astype(np.float32)

        # ── Defragment dataframe memory ──────────────────────────────
        df = df.copy()

        # ── Scale features ───────────────────────────────────────────
        X = self._scaler.transform(df)

        # ── Convert to tensor ────────────────────────────────────────
        tensor = torch.tensor(X, dtype=torch.float32)

        # ── Predict ──────────────────────────────────────────────────
        with torch.no_grad():
            prob = float(self._model(tensor).numpy().flatten()[0])

        prediction = 1 if prob > 0.5 else 0

        return {
            "prediction": prediction,
            "probability": prob,
            "is_winner": bool(prediction),
            "confidence": prob if prediction == 1 else 1 - prob,
            "predicted_party": "Republican" if prediction == 1 else "Democrat",
        }

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def feature_count(self) -> int:
        return len(self._feature_columns) if self._feature_columns else 0


ml_service = MLService()