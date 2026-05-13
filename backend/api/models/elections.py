from sqlalchemy import Column, BigInteger, Boolean, Integer, Text
from api.models.base import Base


class HouseElection(Base):
    __tablename__ = "house_elections"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    year          = Column(BigInteger, index=True)
    state         = Column(Text)
    state_abbr    = Column(Text, index=True)   # e.g. "PA", "CA"
    state_fips    = Column(BigInteger)
    state_cen     = Column(BigInteger)
    state_ic      = Column(BigInteger)
    office        = Column(Text)
    district_num  = Column(BigInteger)
    district_id   = Column(Text, index=True)   # e.g. "PA-07"
    stage         = Column(Text)
    runoff        = Column(Boolean)
    special       = Column(Boolean)
    candidate_name = Column(Text)
    party         = Column(Text)
    party_clean   = Column(Text, index=True)   # "D" | "R" | "OTHER"
    writein       = Column(Boolean)
    mode          = Column(Text)
    candidate_votes = Column(BigInteger)
    total_votes   = Column(BigInteger)
    unofficial    = Column(Boolean)
    version       = Column(BigInteger)
    fusion_ticket = Column(Boolean)