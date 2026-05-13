from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from api.database import get_db
from api.services.data_service import data_service
from api.models import HouseElection

router = APIRouter(prefix="/api/v1", tags=["house_results"])

@router.get("/house-results")
def get_house_results(
    state: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db)
):

    query = db.query(HouseElection)

    if state:
        query = query.filter(
            HouseElection.state_abbr == state
        )

    if year:
        query = query.filter(
            HouseElection.year == year
        )

    total_rows = query.count()

    offset = (page - 1) * limit

    rows = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "data": [
            {
                "year": r.year,
                "state": r.state_abbr,
                "district": r.district_id,
                "candidate": r.candidate_name,
                "party": r.party_clean,
                "votes": r.candidate_votes,
                "total_votes": r.total_votes
            }
            for r in rows
        ],

        "page": page,
        "limit": limit,
        "total_rows": total_rows,
        "total_pages": (
            total_rows + limit - 1
        ) // limit
    }

@router.get("/house-results/meta")
def get_house_metadata(
    db: Session = Depends(get_db)
):

    states = (
        db.query(HouseElection.state_abbr)
        .distinct()
        .order_by(HouseElection.state_abbr)
        .all()
    )

    years = (
        db.query(HouseElection.year)
        .distinct()
        .order_by(HouseElection.year.desc())
        .all()
    )

    return {
        "states": [
            s[0] for s in states if s[0]
        ],

        "years": [
            y[0] for y in years if y[0]
        ]
    }