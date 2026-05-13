from sqlalchemy.orm import Session
from sqlalchemy import func
from api.models import HouseElection, CensusDemographic, StatePVI, PresidentialResult, DistrictHistory
import logging

logger = logging.getLogger(__name__)

class DataService:
    
    @staticmethod
    def get_house_results(db: Session, state: str = None, year: int = None, limit: int = 100):
        query = db.query(HouseElection)
        
        if state:
            query = query.filter(HouseElection.state == state)
        if year:
            query = query.filter(HouseElection.year == year)
        
        total = query.count()
        results = query.limit(limit).all()
        
        return {
            "data": [{
                "year": r.year,
                "state": r.state,
                "state_abbr": r.state_abbr,
                "district": r.district_id,
                "district_num": r.district_num,
                "candidate": r.candidate_name,
                "party": r.party_clean,
                "votes": r.candidate_votes,
                "total_votes": r.total_votes,
                "winner": 1 if r.party_clean == 'R' else 0
            } for r in results],
            "total_rows": total,
            "returned": len(results)
        }
    
    @staticmethod
    def get_census_data(db: Session, limit: int = 100):
        results = db.query(CensusDemographic).limit(limit).all()
        
        return {
            "data": [{
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
                "poverty_rate_pct": r.poverty_rate_pct
            } for r in results],
            "total_rows": db.query(CensusDemographic).count(),
            "returned": len(results)
        }
    
    @staticmethod
    def get_state_pvi(db: Session):
        results = db.query(StatePVI).all()
        
        return {
            "data": [{
                "state": r.state,
                "pvi_score": r.pvi_score,
                "pvi_label": r.pvi_label,
                "state_lean": r.state_lean,
                "avg_dem_pct": r.avg_dem_pct,
                "avg_rep_pct": r.avg_rep_pct
            } for r in results],
            "total_rows": len(results)
        }
    
    @staticmethod
    def get_presidential_results(db: Session, year: int = None, limit: int = 100):
        query = db.query(PresidentialResult)
        
        if year:
            query = query.filter(PresidentialResult.year == year)
        
        results = query.limit(limit).all()
        
        return {
            "data": [{
                "year": r.year,
                "state": r.state,
                "dem_pct": r.dem_pct,
                "rep_pct": r.rep_pct,
                "winner": r.winner
            } for r in results],
            "total_rows": query.count(),
            "returned": len(results)
        }
    
    @staticmethod
    def get_district_history(db: Session, district_id: str):
        result = db.query(DistrictHistory).filter(DistrictHistory.district_id == district_id).first()
        
        if not result:
            return None
        
        history = {}
        for year in [2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024]:
            margin_col = getattr(result, f"margin_{year}", None)
            winner_col = getattr(result, f"winner_{year}", None)
            if margin_col is not None:
                history[year] = {
                    "margin": margin_col,
                    "winner": winner_col
                }
        
        return {
            "district_id": district_id,
            "history": history
        }
    
    @staticmethod
    def get_statistics(db: Session):
        total_elections = db.query(HouseElection).count()
        unique_states = db.query(HouseElection.state).distinct().count()
        
        years = db.query(
            func.min(HouseElection.year), 
            func.max(HouseElection.year)
        ).first()
        
        # Get actual 435 districts (not including header row)
        districts_count = db.query(CensusDemographic).count()
        
        return {
            "total_elections": total_elections,
            "districts": districts_count,
            "states": db.query(StatePVI).count(),
            "years": f"{years[0]}-{years[1]}",
            "unique_states": unique_states,
            "unique_districts": districts_count
        }

data_service = DataService()