from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import DistrictHistory

router = APIRouter(prefix="/api/v1", tags=["history"])

HISTORY_YEARS = [2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024]


@router.get("/district-history/{district_id}")
def get_district_history(district_id: str, db: Session = Depends(get_db)):
    result = (
        db.query(DistrictHistory)
        .filter(DistrictHistory.district_id == district_id.upper())
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail=f"No history for district {district_id}")

    history: dict = {}
    for yr in HISTORY_YEARS:
        margin = getattr(result, f"margin_{yr}", None)
        winner = getattr(result, f"winner_{yr}", None)
        if margin is not None:
            history[str(yr)] = {"margin": margin, "winner": winner}

    return {"district_id": district_id.upper(), "history": history}