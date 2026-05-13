from sqlalchemy import Column, Float, Integer, Text
from api.models.base import Base

class StatePVI(Base):
    __tablename__ = "state_pvi"

    id = Column(Integer, primary_key=True, autoincrement=True)

    state = Column(Text)
    pvi_score = Column(Float)
    pvi_label = Column(Text)
    state_lean = Column(Text)
    avg_dem_pct = Column(Float)
    avg_rep_pct = Column(Float)