import pandas as pd
from neo4j import GraphDatabase
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / "configs" / ".env"

load_dotenv(dotenv_path=ENV_PATH)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD")

print("Loaded URI:", NEO4J_URI)

SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR = SCRIPT_DIR.parent / "election_data"

FILES = {
    "census": DATA_DIR / "census_2024_435_cleaned.csv",
    "house": DATA_DIR / "house_results_cleaned.csv",
    "pvi": DATA_DIR / "state_pvi_cleaned.csv",
    "history": DATA_DIR / "district_history_cleaned.csv"
}

# --- 2. NEO4J INGESTION LOGIC ---
def build_knowledge_graph():
    print("--- Connecting to Neo4j ---")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        driver.verify_connectivity()
        print("✓ Neo4j Connection Successful!\n")
    except Exception as e:
        print(f"[FATAL ERROR] Could not connect to Neo4j: {e}")
        return

    print("Loading cleaned CSVs into memory...")
    df_pvi = pd.read_csv(FILES["pvi"])
    df_history = pd.read_csv(FILES["history"])
    df_census = pd.read_csv(FILES["census"])
    df_house = pd.read_csv(FILES["house"], low_memory=False)

    with driver.session() as session:
        
        print("1/4: Forging State nodes with PVI...")
        for _, row in df_pvi.iterrows():
            session.run("""
                MERGE (s:State {name: $state})
                SET s.pvi_score = $pvi_score,
                    s.pvi_label = $pvi_label,
                    s.lean = $state_lean
            """, state=row['state'], pvi_score=row['pvi_score'], 
                 pvi_label=row['pvi_label'], state_lean=row['state_lean'])

        print("2/4: Forging all 461 Historical District nodes...")
        for _, row in df_history.iterrows():
            session.run("""
                MERGE (d:District {id: $dist_id})
                SET d.status = 'historical'
            """, dist_id=row['district_id'])

        print("3/4: Activating current 435 Districts and applying Census data...")
        for _, row in df_census.iterrows():
            session.run("""
                MATCH (d:District {id: $dist_id})
                SET d.status = 'active',
                    d.total_population = $pop,
                    d.median_age = $age,
                    d.median_income = $income
                WITH d
                MATCH (s:State {name: $state_name})
                MERGE (d)-[:LOCATED_IN]->(s)
            """, dist_id=row['district_id'], pop=row.get('total_population'), 
                 age=row.get('median_age'), income=row.get('median_household_income'),
                 state_name=row['state'])

        print("4/4: Forging Candidates and Election Edges (2012-2024)...")
        df_modern = df_house[df_house['year'] >= 2012] 
        
        for _, row in df_modern.iterrows():
            if pd.isna(row['district_id']): continue
            
            # Extracting the math out of the Cypher block to prevent syntax errors
            candidate_votes = int(row['candidate_votes'])
            total_votes = int(row['total_votes'])
            v_pct = round((candidate_votes / total_votes) * 100, 2) if total_votes > 0 else 0.0
            
            session.run("""
                MATCH (d:District {id: $dist_id})
                MERGE (c:Candidate {name: $candidate_name})
                ON CREATE SET c.party = $party
                
                MERGE (c)-[r:RAN_IN {year: $year}]->(d)
                SET r.votes = $votes,
                    r.total_votes = $total,
                    r.vote_pct = $vote_pct
            """, dist_id=row['district_id'], 
                 candidate_name=row['candidate_name'], 
                 party=row['party_clean'], 
                 year=int(row['year']), 
                 votes=candidate_votes, 
                 total=total_votes,
                 vote_pct=v_pct)
                 
    driver.close()
    print("\n--- PHASE 1 COMPLETE: Neo4j Knowledge Graph Successfully Built! ---")

if __name__ == "__main__":
    build_knowledge_graph()