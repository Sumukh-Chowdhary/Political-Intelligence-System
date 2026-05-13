"""
Data loading pipeline.

Run from backend/ directory:
    python scripts/load_data.py            # load all tables
    python scripts/load_data.py house      # load only house_elections
    python scripts/load_data.py census pvi # load two tables

Tables: house | census | pvi | presidential | history

Flow:
  1. Read CSV with pandas
  2. Rename columns to match SQLAlchemy model (see COLUMN_MAPS below)
  3. Drop columns not in the model, fill missing model columns with None
  4. Bulk-insert via pandas to_sql (fast — uses COPY protocol on Postgres)

To add a new dataset later:
  - Add a new entry to LOADERS dict at the bottom of this file.
  - Done.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from sqlalchemy import text
from api.database import engine
from api.config import Config
from api.models import (
    Base,
    HouseElection,
    CensusDemographic,
    StatePVI,
    PresidentialResult,
    DistrictHistory,
)
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)


# ── Column rename maps ────────────────────────────────────────────────────────
# Keys = CSV column names, Values = SQLAlchemy model column names.
# Only list columns that actually differ — identical names are auto-kept.
# Add/remove entries here whenever your CSV changes.

HOUSE_RENAMES = {
    # MIT Election Lab common column names → our model names
    "state_po":       "state_abbr",
    "candidate":      "candidate_name",
    "candidatevotes": "candidate_votes",
    "totalvotes":     "total_votes",
    "district":       "district_num",
    # If your cleaned CSV already uses our names, these are no-ops:
    "state_abbr":     "state_abbr",
    "candidate_name": "candidate_name",
    "candidate_votes": "candidate_votes",
    "total_votes":    "total_votes",
    "district_num":   "district_num",
}

CENSUS_RENAMES: dict = {}      # add if CSV columns differ from model
PVI_RENAMES: dict = {}
PRESIDENTIAL_RENAMES: dict = {}
HISTORY_RENAMES: dict = {}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _model_columns(model) -> list[str]:
    """Return all column names for a model, excluding the auto-PK 'id'."""
    return [
        col.key
        for col in model.__table__.columns
        if col.key != "id"
    ]


def _load_csv(
    csv_path: Path,
    model,
    rename_map: dict,
    table_name: str,
    truncate: bool = True,
) -> None:
    if not csv_path.exists():
        log.error(f"CSV not found: {csv_path}")
        return

    log.info(f"Reading {csv_path.name} …")
    df = pd.read_csv(csv_path, low_memory=False)
    log.info(f"  {len(df):,} rows × {len(df.columns)} columns loaded from CSV")

    # 1. Rename columns so they match model names
    df = df.rename(columns=rename_map)

    # 2. Keep only columns that exist in the model
    model_cols = _model_columns(model)
    keep = [c for c in model_cols if c in df.columns]
    missing = [c for c in model_cols if c not in df.columns]
    df = df[keep].copy()

    if missing:
        log.warning(f"  Columns not found in CSV (will be NULL): {missing}")

    # 3. Coerce boolean-ish columns (True/False strings → bool)
    for col in df.select_dtypes(include="object").columns:
        sample = df[col].dropna().astype(str).str.lower().unique()
        if set(sample).issubset({"true", "false", "1", "0", "yes", "no", ""}):
            df[col] = df[col].map(
                lambda v: True if str(v).lower() in ("true", "1", "yes")
                else (False if str(v).lower() in ("false", "0", "no") else None)
            )

    # 4. Truncate existing rows then bulk-insert
    with engine.begin() as conn:
        if truncate:
            conn.execute(text(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE'))
            log.info(f"  Truncated {table_name}")

    df.to_sql(
        table_name,
        engine,
        if_exists="append",    # table already exists (created by create_tables.py)
        index=False,
        method="multi",        # batched INSERT — change to 'None' for single-row if needed
        chunksize=500,
    )
    log.info(f"  ✓ Inserted {len(df):,} rows into {table_name}\n")


# ── Individual loaders ────────────────────────────────────────────────────────

def load_house():
    _load_csv(Config.HOUSE_CSV, HouseElection, HOUSE_RENAMES, "house_elections")


def load_census():
    _load_csv(Config.CENSUS_CSV, CensusDemographic, CENSUS_RENAMES, "census_demographics")


def load_pvi():
    _load_csv(Config.PVI_CSV, StatePVI, PVI_RENAMES, "state_pvi")


def load_presidential():
    _load_csv(Config.PRESIDENTIAL_CSV, PresidentialResult, PRESIDENTIAL_RENAMES, "presidential_results")


def load_history():
    _load_csv(Config.HISTORY_CSV, DistrictHistory, HISTORY_RENAMES, "district_history")


# ── Registry — add new datasets here ─────────────────────────────────────────
LOADERS: dict[str, callable] = {
    "house":        load_house,
    "census":       load_census,
    "pvi":          load_pvi,
    "presidential": load_presidential,
    "history":      load_history,
}


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    targets = args if args else list(LOADERS.keys())

    unknown = [t for t in targets if t not in LOADERS]
    if unknown:
        log.error(f"Unknown target(s): {unknown}. Valid: {list(LOADERS.keys())}")
        sys.exit(1)

    log.info(f"Loading: {targets}\n")
    for name in targets:
        log.info(f"=== {name.upper()} ===")
        LOADERS[name]()

    log.info("✅  All requested tables loaded successfully.")


if __name__ == "__main__":
    main()