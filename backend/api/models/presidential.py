from sqlalchemy import Column, Float, Integer, BigInteger, Text
from api.models.base import Base

class PresidentialResult(Base):
    __tablename__ = "presidential_results"

    id = Column(Integer, primary_key=True, autoincrement=True)

    year = Column(BigInteger)
    state = Column(Text)
    dem_pct = Column(Float)
    rep_pct = Column(Float)
    winner = Column(Text)