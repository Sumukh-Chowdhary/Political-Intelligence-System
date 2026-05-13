from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import CensusDemographic

router = APIRouter(prefix="/api/v1", tags=["census"])


@router.get("/census-data")
def get_census_data(
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    total = db.query(CensusDemographic).count()
    offset = (page - 1) * limit
    results = db.query(CensusDemographic).offset(offset).limit(limit).all()

    return {
        "data": [
            {
                "district_id": r.district_id,
                "district_name": r.district_name,
                "total_population": r.total_population,
                "median_age": r.median_age,
                "white_pct": r.white_pct,
                "black_pct": r.black_pct,
                "hispanic_pct": r.hispanic_pct,
                "asian_pct": r.asian_pct,
                "median_household_income": r.median_household_income,
                "college_grad_pct": r.college_grad_pct,
                "poverty_rate_pct": r.poverty_rate_pct,
                "unemployment_rate_pct": r.unemployment_rate_pct,
                "veteran_pct": r.veteran_pct,
            }
            for r in results
        ],
        "page": page,
        "limit": limit,
        "total_rows": total,
        "total_pages": max(1, (total + limit - 1) // limit),
        "returned": len(results),
    }