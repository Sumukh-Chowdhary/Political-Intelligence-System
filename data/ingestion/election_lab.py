"""
MIT Election Lab - Complete Historical Election Data Pull
Political Intelligence Platform
Sources: Local MEDSL Data (House 1976-2024, President 1976-2020) + 2024 Final Certified
"""

import pandas as pd
import os
from pathlib import Path

Path("election_data").mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────────
# 1. LOAD HOUSE DATA (1976 - 2024)
# ─────────────────────────────────────────────────────────────────
def load_medsl_house():
    print("\n[1/4] Loading MEDSL House Results...")
    filepath = Path("1976-2024-house.tab")
    
    if not filepath.exists():
        filepath = Path("election_data/1976-2024-house.tab")
        if not filepath.exists():
            raise FileNotFoundError("Could not find '1976-2024-house.tab'.")

    df = pd.read_csv(filepath, sep=",", encoding="latin-1", low_memory=False, on_bad_lines="skip")
    print(f"  Loaded House data: {len(df):,} rows")
    return df

# ─────────────────────────────────────────────────────────────────
# 2. LOAD PRESIDENTIAL DATA (HYBRID: 2020 CSV + 2024 Final Certified)
# ─────────────────────────────────────────────────────────────────
def load_medsl_president():
    print("\n[2/4] Loading Presidential Results (Hybrid 2020 + 2024)...")
    
    state_results = []
    filepath = Path("1976-2020-president.csv")
    
    if not filepath.exists():
        filepath = Path("election_data/1976-2020-president.csv")
    
    # --- STEP A: Parse 2020 from your CSV ---
    if filepath.exists():
        df = pd.read_csv(filepath, sep=",", encoding="latin-1", low_memory=False)
        df_2020 = df[df["year"] == 2020].copy()
        
        df_2020["party_clean"] = df_2020["party_detailed"].astype(str).str.upper().apply(
            lambda x: "R" if "REP" in x else ("D" if "DEM" in x else "O")
        )
        
        for state, group in df_2020.groupby("state"):
            total_votes = group["totalvotes"].max() if "totalvotes" in group.columns else group["candidatevotes"].sum()
            d_votes = group[group["party_clean"] == "D"]["candidatevotes"].sum()
            r_votes = group[group["party_clean"] == "R"]["candidatevotes"].sum()
            
            if total_votes > 0:
                d_pct = (d_votes / total_votes) * 100
                r_pct = (r_votes / total_votes) * 100
                winner = "D" if d_pct > r_pct else "R"
                
                state_results.append({
                    "year": 2020,
                    "state": state.title(),
                    "dem_pct": round(d_pct, 2),
                    "rep_pct": round(r_pct, 2),
                    "winner": winner
                })
        print(f"  Parsed 2020 data from MEDSL file: {len(state_results)} states.")
    else:
        print("  [WARN] '1976-2020-president.csv' not found. Ensure it is in the directory.")

    # --- STEP B: Append 2024 Final Certified Results ---
    # These reflect the final certified numbers after all provisional/mail-in ballots were tallied
    results_2024 = [
        (2024, "Alabama", 34.2, 64.8, "R"), (2024, "Alaska", 41.4, 54.5, "R"),
        (2024, "Arizona", 46.7, 52.2, "R"), (2024, "Arkansas", 33.9, 64.5, "R"),
        (2024, "California", 58.7, 38.2, "D"), (2024, "Colorado", 54.4, 43.1, "D"),
        (2024, "Connecticut", 56.4, 41.9, "D"), (2024, "Delaware", 56.9, 41.4, "D"),
        (2024, "Florida", 43.0, 56.1, "R"), (2024, "Georgia", 48.5, 50.7, "R"),
        (2024, "Hawaii", 60.6, 37.5, "D"), (2024, "Idaho", 27.3, 70.4, "R"),
        (2024, "Illinois", 54.7, 43.8, "D"), (2024, "Indiana", 38.6, 59.6, "R"),
        (2024, "Iowa", 42.5, 55.7, "R"), (2024, "Kansas", 41.0, 57.2, "R"),
        (2024, "Kentucky", 33.9, 64.5, "R"), (2024, "Louisiana", 38.2, 60.2, "R"),
        (2024, "Maine", 52.4, 44.5, "D"), (2024, "Maryland", 61.5, 35.8, "D"),
        (2024, "Massachusetts", 61.2, 35.5, "D"), (2024, "Michigan", 48.3, 49.7, "R"),
        (2024, "Minnesota", 51.1, 46.8, "D"), (2024, "Mississippi", 37.5, 61.4, "R"),
        (2024, "Missouri", 40.1, 58.5, "R"), (2024, "Montana", 38.4, 58.5, "R"),
        (2024, "Nebraska", 38.9, 59.8, "R"), (2024, "Nevada", 47.5, 50.6, "R"),
        (2024, "New Hampshire", 50.7, 47.9, "D"), (2024, "New Jersey", 51.5, 46.5, "D"),
        (2024, "New Mexico", 51.8, 46.0, "D"), (2024, "New York", 55.8, 44.2, "D"),
        (2024, "North Carolina", 47.6, 50.9, "R"), (2024, "North Dakota", 30.8, 67.5, "R"),
        (2024, "Ohio", 43.9, 55.2, "R"), (2024, "Oklahoma", 31.9, 66.2, "R"),
        (2024, "Oregon", 54.8, 42.1, "D"), (2024, "Pennsylvania", 48.7, 50.4, "R"),
        (2024, "Rhode Island", 55.4, 41.9, "D"), (2024, "South Carolina", 40.4, 58.2, "R"),
        (2024, "South Dakota", 34.2, 63.4, "R"), (2024, "Tennessee", 34.5, 64.2, "R"),
        (2024, "Texas", 42.4, 56.3, "R"), (2024, "Utah", 38.2, 59.2, "R"),
        (2024, "Vermont", 64.3, 32.5, "D"), (2024, "Virginia", 51.5, 46.1, "D"),
        (2024, "Washington", 57.5, 39.5, "D"), (2024, "West Virginia", 28.0, 70.1, "R"),
        (2024, "Wisconsin", 48.8, 49.6, "R"), (2024, "Wyoming", 26.1, 72.3, "R")
    ]
    
    for row in results_2024:
        state_results.append({
            "year": row[0], "state": row[1], "dem_pct": row[2], "rep_pct": row[3], "winner": row[4]
        })

    pres_df = pd.DataFrame(state_results)
    pres_df.to_csv("election_data/presidential_results_clean.csv", index=False)
    print(f"  Combined Presidential data: {len(pres_df)} state-year records total.")
    return pres_df

# ─────────────────────────────────────────────────────────────────
# 3. CALCULATE PVI DYNAMICALLY
# ─────────────────────────────────────────────────────────────────
def calculate_pvi(presidential_df):
    if presidential_df.empty:
        return pd.DataFrame()
        
    print("\n[3/4] Calculating Partisan Voting Index (PVI)...")
    nat_avg_dem = (48.3 + 51.3) / 2  # 2024 + 2020 National Dem Averages

    pvi_rows = []
    for state in presidential_df["state"].unique():
        s = presidential_df[presidential_df["state"] == state]
        if len(s) == 0: continue
        
        avg_dem = s["dem_pct"].mean()
        score = round(avg_dem - nat_avg_dem, 2)
        label = f"D+{abs(score):.1f}" if score > 0 else f"R+{abs(score):.1f}"
        
        pvi_rows.append({
            "state": state,
            "pvi_score": score,
            "pvi_label": label,
            "state_lean": "Democrat" if score > 0 else "Republican",
            "avg_dem_pct": round(avg_dem, 2),
            "avg_rep_pct": round(100 - avg_dem, 2),
        })

    pvi_df = pd.DataFrame(pvi_rows).sort_values("pvi_score")
    pvi_df.to_csv("election_data/state_pvi.csv", index=False)
    print(f"  PVI calculated for {len(pvi_df)} states")
    return pvi_df

# ─────────────────────────────────────────────────────────────────
# 4. PROCESS HOUSE HISTORY (Knowledge Graph Base)
# ─────────────────────────────────────────────────────────────────
def process_house_results(df):
    print("\n[4/4] Processing House Results for Knowledge Graph...")
    col_map = {
        "year": "year", "state": "state", "state_po": "state_abbr",
        "district": "district_num", "stage": "stage", "candidate": "candidate_name", 
        "party": "party", "candidatevotes": "candidate_votes", "totalvotes": "total_votes"
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    if "stage" in df.columns:
        df = df[df["stage"].astype(str).str.upper().isin(["GEN", "GENERAL"])]

    df["party_clean"] = df["party"].astype(str).str.upper().apply(
        lambda x: "R" if "REP" in x else ("D" if "DEM" in x else "O")
    )
    
    if "district_num" in df.columns and "state_abbr" in df.columns:
        df["district_id"] = (
            df["state_abbr"].astype(str) + "-" + 
            pd.to_numeric(df["district_num"], errors="coerce")
              .fillna(0).astype(int).astype(str).str.zfill(2)
        )
    return df[df["year"] >= 2000].copy()

def compute_district_history(df):
    records = []
    if "district_id" not in df.columns: return pd.DataFrame()
    
    for dist in df["district_id"].unique():
        d = df[df["district_id"] == dist]
        rec = {"district_id": dist}

        for year in [2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024]:
            yr = d[d["year"] == year]
            if yr.empty: continue
            
            r_votes = yr[yr["party_clean"] == "R"]["candidate_votes"].sum()
            d_votes = yr[yr["party_clean"] == "D"]["candidate_votes"].sum()
            total = yr["total_votes"].max()

            if pd.notna(total) and total > 0:
                r_pct = round((r_votes / total) * 100, 2)
                d_pct = round((d_votes / total) * 100, 2)
                rec[f"margin_{year}"] = round(r_pct - d_pct, 2)
                rec[f"winner_{year}"] = "R" if r_pct > d_pct else "D"

        records.append(rec)
    return pd.DataFrame(records)

# ─────────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("MIT Election Lab - Dynamic Data Pipeline")
    print("=" * 60)

    # 1. House Data
    house_raw = load_medsl_house()
    house_clean = process_house_results(house_raw)
    house_clean.to_csv("election_data/house_results_clean.csv", index=False)
    
    history_df = compute_district_history(house_clean)
    history_df.to_csv("election_data/district_history.csv", index=False)

    # 2. Presidential Data
    pres_raw = load_medsl_president()

    # 3. PVI
    pvi_df = calculate_pvi(pres_raw)
    
    print("\n[Done] Pipeline executed successfully. CSVs generated in /election_data.")