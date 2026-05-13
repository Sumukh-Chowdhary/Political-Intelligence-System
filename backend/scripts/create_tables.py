"""
Run from backend/ directory:
    python scripts/create_tables.py

Drops ALL tables managed by SQLAlchemy then recreates them.
Safe to re-run any time — completely idempotent.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# ── load .env from backend/ directory ─────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ── make sure `api` package is importable ─────────────────────────
sys.path.insert(0, str(BASE_DIR))

from api.database import engine
from api.models import Base   # imports all model classes automatically


# ── order matters for FK constraints, but Base handles it automatically ──────

def main():
    print("⚠  Dropping all tables …")
    Base.metadata.drop_all(bind=engine)
    print("✓  All tables dropped.")

    print("⚙  Creating tables …")
    Base.metadata.create_all(bind=engine)

    print("✓  Tables created:")
    for table in Base.metadata.sorted_tables:
        print(f"   • {table.name}")

    print("\n✅  Done — database is ready for data loading.")


if __name__ == "__main__":
    main()