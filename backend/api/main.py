from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import Config
from api.routes import health, predictions, metrics, house_results, census, pvi, statistics, history
from api.services.ml_service import ml_service
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Political Intelligence API",
    description="ML model serving and election data API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────────────────
# Order matters: more-specific paths BEFORE wildcard paths inside each router
app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(statistics.router)
app.include_router(house_results.router)
app.include_router(census.router)
app.include_router(pvi.router)
app.include_router(history.router)
app.include_router(predictions.router)   # predictions last — has /{district_id} wildcard


@app.on_event("startup")
async def startup_event():
    logger.info("Loading ML model …")
    ok = ml_service.load()
    if ok:
        logger.info(f"Model loaded — {ml_service.feature_count} features")
    else:
        logger.warning("Model failed to load — predictions will use fallback logic")


@app.get("/")
def root():
    return {
        "message": "Political Intelligence System API",
        "docs": "/docs",
        "version": "1.0.0",
    }