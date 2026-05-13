from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.database import get_db
from api.services.data_service import data_service

router = APIRouter(prefix="/api/v1", tags=["statistics"])

@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db)):
    return data_service.get_statistics(db)