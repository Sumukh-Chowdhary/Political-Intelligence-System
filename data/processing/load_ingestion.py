import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

# Connection String
PG_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- DIRECTORY SETUP ---
SCRIPT_DIR = Path(__file__).parent.resolve()  # Gets data/processing/
DATA_DIR = SCRIPT_DIR.parent / "election_data"  # Navigates to data/election_data/

# Map the cleaned CSV files to their new PostgreSQL Table names
TABLE_MAPPINGS = {
    "census_demographics": DATA_DIR / "census_2024_435_cleaned.csv",
    "house_elections": DATA_DIR / "house_results_cleaned.csv",
    "state_pvi": DATA_DIR / "state_pvi_cleaned.csv",
    "presidential_results": DATA_DIR / "presidential_results_cleaned.csv",
    "district_history": DATA_DIR / "district_history_cleaned.csv"
}

def load_to_postgres():
    print(f"--- Connecting to PostgreSQL Database: {DB_NAME} ---")
    
    try:
        # Create the database engine
        engine = create_engine(PG_URI)
        
        # Test connection
        with engine.connect() as conn:
            print("✓ Connection successful!\n")
            
            for table_name, file_path in TABLE_MAPPINGS.items():
                if file_path.exists():
                    print(f"Reading {file_path.name}...")
                    
                    # Read the cleaned CSV
                    df = pd.read_csv(file_path, low_memory=False)
                    
                    # Push to Postgres
                    # if_exists='replace' creates the table from scratch and infers data types
                    print(f"  -> Pushing {len(df)} rows to table '{table_name}'...")
                    df.to_sql(table_name, engine, if_exists='replace', index=False)
                    print(f"  ✓ Successfully created and populated '{table_name}'.\n")
                else:
                    print(f"[ERROR] Could not find {file_path.name} in {DATA_DIR}")

            # Optional Pro-Move: Add Primary Keys to the static tables for faster querying
            print("--- Optimizing Database Schema ---")
            try:
                conn.execute(text("ALTER TABLE state_pvi ADD PRIMARY KEY (state);"))
                conn.execute(text("ALTER TABLE census_demographics ADD PRIMARY KEY (district_id);"))
                conn.execute(text("ALTER TABLE district_history ADD PRIMARY KEY (district_id);"))
                conn.commit()
                print("✓ Primary Keys assigned to static tables.")
            except Exception as e:
                # If PKs fail (e.g. running script twice), just pass gracefully
                print("Note: Primary keys already exist or couldn't be applied. Skipping optimization.")

        print("\n--- PHASE 1: STRUCTURED DB LOAD COMPLETE ---")
        
    except Exception as e:
        print(f"\n[FATAL ERROR] Could not connect to the database. Check your credentials.")
        print(f"Details: {e}")

if __name__ == "__main__":
    load_to_postgres()