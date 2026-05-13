"""
Prediction routes.

Route ordering is critical in FastAPI — literal paths must come BEFORE
wildcard paths.  Order here:
  1. GET /predictions/summary
  2. GET /predictions/state/{state}
  3. GET /predictions              (list)
  4. GET /predictions/{district_id}  ← wildcard, always last
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from api.database import get_db
from api.models import HouseElection
from api.services.ml_service import ml_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["predictions"])


# ── helpers ──────────────────────────────────────────────────────────────────

def _winner_rows(db: Session, year: int, state: Optional[str] = None):
    """
    Return one row per district — the candidate with the most votes.
    Uses a subquery so we always get the actual winner, not a random row.
    """
    sub = (
        db.query(
            HouseElection.district_id,
            func.max(HouseElection.candidate_votes).label("max_votes"),
        )
        .filter(
            HouseElection.year == year,
            HouseElection.party_clean.in_(["D", "R"]),
        )
        .group_by(HouseElection.district_id)
        .subquery()
    )

    q = (
        db.query(HouseElection)
        .join(
            sub,
            (HouseElection.district_id == sub.c.district_id)
            & (HouseElection.candidate_votes == sub.c.max_votes),
        )
        .filter(
            HouseElection.year == year,
            #HouseElection.party_clean.in_(["D", "R"]),
        )
    )

    if state:
        q = q.filter(HouseElection.state_abbr == state)

    return q.order_by(HouseElection.district_id)


def _row_to_prediction(row: HouseElection) -> dict:
    predicted_winner = "Democrat" if row.party_clean == "D" else "Republican"

    # Use ML model if loaded, otherwise fall back to historical result
    probability = 0.65
    if ml_service.is_loaded:
        try:
            result = ml_service.predict({
                "year": row.year,
                "candidate_votes": row.candidate_votes,
                "total_votes": row.total_votes,
                "district_id": row.district_id,
                "state_abbr": row.state_abbr,
            })
            probability = result["confidence"]
        except Exception:
            pass  # silently fall back

    return {
        "district": row.district_id,
        "state": row.state_abbr,
        "year": row.year,
        "predicted_winner": predicted_winner,
        "win_probability": round(probability, 4),
        "confidence": round(probability, 4),
        "features_used": ml_service.feature_count,
    }


# ── 1. summary — MUST be before /{district_id} ───────────────────────────────

@router.get("/predictions/summary")
def get_predictions_summary(year: int = Query(2024), db: Session = Depends(get_db)):
    try:
        rows = _winner_rows(db, year).all()
        dem = sum(1 for r in rows if r.party_clean == "D")
        rep = sum(1 for r in rows if r.party_clean == "R")
        total = dem + rep
        return {
            "year": year,
            "total_districts_processed": total,
            "democrat_projections": dem,
            "republican_projections": rep,
            "democrat_percentage": round(dem / total * 100, 2) if total else 0,
            "republican_percentage": round(rep / total * 100, 2) if total else 0,
        }
    except Exception as e:
        logger.error(f"Summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── 2. by state — MUST be before /{district_id} ──────────────────────────────

@router.get("/predictions/state/{state}")
def get_predictions_by_state(
    state: str,
    year: int = Query(2024),
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=500),
    db: Session = Depends(get_db),
):
    try:
        q = _winner_rows(db, year, state=state.upper())

        total = q.count()

        offset = (page - 1) * limit

        rows = q.offset(offset).limit(limit).all()

        return {
            "data": [_row_to_prediction(r) for r in rows],
            "page": page,
            "limit": limit,
            "total_rows": total,
            "total_pages": max(1, (total + limit - 1) // limit),
            "state": state.upper(),
        }

    except Exception as e:
        logger.error(f"State predictions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── 3. list (paginated) ───────────────────────────────────────────────────────

@router.get("/predictions")
def get_predictions(
    state: Optional[str] = Query(None),
    year: int = Query(2024),
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=500),
    db: Session = Depends(get_db),
):
    try:
        q = _winner_rows(db, year, state=state.upper() if state else None)
        total = q.count()
        offset = (page - 1) * limit
        rows = q.offset(offset).limit(limit).all()

        districts = [r.district_id for r in rows]

        return {
            "data": [_row_to_prediction(r) for r in rows],
            "page": page,
            "limit": limit,
            "total_rows": total,
            "total_pages": max(1, (total + limit - 1) // limit),
        }
    except Exception as e:
        logger.error(f"Predictions list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── 4. single district — wildcard, MUST be last ───────────────────────────────

@router.get("/predictions/{district_id}")
def get_district_prediction(
    district_id: str,
    year: int = Query(2024),
    db: Session = Depends(get_db),
):
    try:
        row = (
            _winner_rows(db, year)
            .filter(HouseElection.district_id == district_id.upper())
            .first()
        )
        if not row:
            raise HTTPException(status_code=404, detail=f"District {district_id} not found for {year}")
        return _row_to_prediction(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"District prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))