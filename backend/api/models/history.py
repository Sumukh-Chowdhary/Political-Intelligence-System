from sqlalchemy import Column, Float, Text, Integer
from api.models.base import Base

class DistrictHistory(Base):
    __tablename__ = "district_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    district_id = Column(Text)

    margin_2004 = Column(Float)
    winner_2004 = Column(Text)

    margin_2006 = Column(Float)
    winner_2006 = Column(Text)

    margin_2008 = Column(Float)
    winner_2008 = Column(Text)

    margin_2010 = Column(Float)
    winner_2010 = Column(Text)

    margin_2012 = Column(Float)
    winner_2012 = Column(Text)

    margin_2014 = Column(Float)
    winner_2014 = Column(Text)

    margin_2016 = Column(Float)
    winner_2016 = Column(Text)

    margin_2018 = Column(Float)
    winner_2018 = Column(Text)

    margin_2020 = Column(Float)
    winner_2020 = Column(Text)

    margin_2022 = Column(Float)
    winner_2022 = Column(Text)

    margin_2024 = Column(Float)
    winner_2024 = Column(Text)