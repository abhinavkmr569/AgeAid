import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# 1. Get URL and fix for CockroachDB
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "cockroachdb://", 1)

# 2. Connect
engine = create_engine(DATABASE_URL)

print("☢️  INITIATING NUCLEAR RESET...")

with engine.connect() as conn:
    # A. Force drop the Alembic Version table (The Zombie)
    try:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE;"))
        print("✅ Killed Zombie Migration (alembic_version dropped).")
    except Exception as e:
        print(f"⚠️ Could not drop alembic_version: {e}")

    # B. Drop all other tables
    tables = ["test_results", "patient_reports", "users"]
    for t in tables:
        try:
            conn.execute(text(f"DROP TABLE IF EXISTS {t} CASCADE;"))
            print(f"✅ Dropped table: {t}")
        except Exception as e:
            print(f"⚠️ Error dropping {t}: {e}")
            
    conn.commit()

print("✨ Database is 100% empty. Ready for fresh start.")