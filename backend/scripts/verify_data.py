from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

PG_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(PG_URI)

with engine.connect() as conn:
    tables = ['house_elections', 'census_demographics', 'state_pvi', 'presidential_results', 'district_history']
    
    print("=" * 50)
    print("DATABASE VERIFICATION")
    print("=" * 50)
    
    for table in tables:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count = result.scalar()
        print(f"✓ {table}: {count} rows")
    
    print("\n" + "=" * 50)
    print("SAMPLE DATA")
    print("=" * 50)
    
    # Sample from house_elections
    result = conn.execute(text("SELECT year, state, district_id, party_clean FROM house_elections LIMIT 5"))
    print("\nHouse Elections Sample:")
    for row in result:
        print(f"  {row.year} - {row.state} - {row.district_id} - {row.party_clean}")
    
    # Sample from census
    result = conn.execute(text("SELECT district_id, total_population, median_age FROM census_demographics LIMIT 5"))
    print("\nCensus Sample:")
    for row in result:
        print(f"  {row.district_id}: Pop={row.total_population}, Median Age={row.median_age}")