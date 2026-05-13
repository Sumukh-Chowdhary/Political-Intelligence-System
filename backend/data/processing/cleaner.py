import pandas as pd
import re
import os
from pathlib import Path

# --- DIRECTORY SETUP ---
# This automatically finds the 'data/election_data' folder based on where the script is located
SCRIPT_DIR = Path(__file__).parent.resolve()  # Gets data/processing/
DATA_DIR = SCRIPT_DIR.parent / "election_data"  # Navigates to data/election_data/

# --- STATE MAPPING ---
STATE_TO_ABBR = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
    'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
    'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN',
    'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

# --- CLEANING FUNCTIONS ---

def clean_census_data(in_file, out_file):
    print(f"Cleaning: {in_file.name} -> {out_file.name}")
    df = pd.read_csv(in_file)
    
    def parse_district_id(row):
        name_str = str(row.get('district_name', ''))
        
        state = None
        for s in STATE_TO_ABBR.keys():
            if s in name_str:
                state = STATE_TO_ABBR[s]
                break
                
        if "(at Large)" in name_str or "At Large" in name_str:
            dist_num = "00"
        else:
            match = re.search(r'District (\d+)', name_str)
            dist_num = str(match.group(1)).zfill(2) if match else "00"
            
        if state:
            return f"{state}-{dist_num}"
        return None

    df['district_id'] = df.apply(parse_district_id, axis=1)
    df = df.dropna(subset=['district_id'])
    
    # Reorder columns to put district_id first for easy inspection
    cols = ['district_id'] + [c for c in df.columns if c != 'district_id']
    df = df[cols]
    
    df.to_csv(out_file, index=False)
    return len(df)

def clean_house_results(in_file, out_file):
    print(f"Cleaning: {in_file.name} -> {out_file.name}")
    df = pd.read_csv(in_file, low_memory=False)
    
    df = df.dropna(subset=['candidate_votes', 'total_votes'])
    
    df['candidate_votes'] = df['candidate_votes'].astype(int)
    df['total_votes'] = df['total_votes'].astype(int)
    df['year'] = df['year'].astype(int)
    
    df['state'] = df['state'].str.title()
    df['candidate_name'] = df['candidate_name'].str.title()
    
    df.to_csv(out_file, index=False)
    return len(df)

def clean_pvi_and_presidential(pvi_in, pres_in, pvi_out, pres_out):
    print(f"Cleaning: {pvi_in.name} -> {pvi_out.name}")
    pvi_df = pd.read_csv(pvi_in)
    pvi_df['state'] = pvi_df['state'].str.title()
    pvi_df.to_csv(pvi_out, index=False)
    
    print(f"Cleaning: {pres_in.name} -> {pres_out.name}")
    pres_df = pd.read_csv(pres_in)
    pres_df['state'] = pres_df['state'].str.title()
    pres_df.to_csv(pres_out, index=False)
    
    return len(pvi_df), len(pres_df)

def clean_district_history(in_file, out_file):
    print(f"Cleaning: {in_file.name} -> {out_file.name}")
    df = pd.read_csv(in_file)
    
    df['district_id'] = df['district_id'].str.strip().str.upper()
    
    df.to_csv(out_file, index=False)
    return len(df)

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print(f"--- Starting Data Cleaning Process ---")
    print(f"Looking for data in: {DATA_DIR}\n")
    
    # Define file paths using Pathlib
    files = {
        "census": DATA_DIR / "census_2024_435.csv",
        "house": DATA_DIR / "house_results_clean.csv",
        "pvi": DATA_DIR / "state_pvi.csv",
        "pres": DATA_DIR / "presidential_results_clean.csv",
        "history": DATA_DIR / "district_history.csv"
    }
    
    missing_files = [f.name for f in files.values() if not f.exists()]
    
    if missing_files:
        print(f"ERROR: Missing the following files in {DATA_DIR}: {missing_files}")
    else:
        c_count = clean_census_data(files["census"], DATA_DIR / "census_2024_435_cleaned.csv")
        h_count = clean_house_results(files["house"], DATA_DIR / "house_results_cleaned.csv")
        pvi_count, pres_count = clean_pvi_and_presidential(
            files["pvi"], files["pres"],
            DATA_DIR / "state_pvi_cleaned.csv", DATA_DIR / "presidential_results_cleaned.csv"
        )
        dh_count = clean_district_history(files["history"], DATA_DIR / "district_history_cleaned.csv")
        
        print("\n--- Cleaning Complete ---")
        print(f"Census Rows: {c_count}")
        print(f"House Result Rows: {h_count}")
        print(f"State PVI Rows: {pvi_count}")
        print(f"Presidential Rows: {pres_count}")
        print(f"District History Rows: {dh_count}")
        print("\nReview the new '_cleaned.csv' files in your data/election_data/ folder!")