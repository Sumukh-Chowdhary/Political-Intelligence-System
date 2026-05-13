from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import StatePVI

router = APIRouter(prefix="/api/v1", tags=["pvi"])


@router.get("/state-pvi")
def get_state_pvi(
    page: int = Query(1, ge=1),
    limit: int = Query(60, le=60),   # max 50 states + DC
    db: Session = Depends(get_db),
):
    total = db.query(StatePVI).count()
    offset = (page - 1) * limit
    results = db.query(StatePVI).order_by(StatePVI.state).offset(offset).limit(limit).all()

    return {
        "data": [
            {
                "state": r.state,
                "pvi_score": r.pvi_score,
                "pvi_label": r.pvi_label,
                "state_lean": r.state_lean,
                "avg_dem_pct": r.avg_dem_pct,
                "avg_rep_pct": r.avg_rep_pct,
            }
            for r in results
        ],
        "page": page,
        "limit": limit,
        "total_rows": total,
        "total_pages": max(1, (total + limit - 1) // limit),
        "returned": len(results),
    }