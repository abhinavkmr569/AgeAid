import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# 1. Get URL
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "cockroachdb://", 1)

# 2. Connect
engine = create_engine(DATABASE_URL)

# 3. Drop Tables (Reset)
print("💥 Dropping old tables...")
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS test_results CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS patient_reports CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
    # --- CRITICAL NEW LINE ---
    conn.execute(text("DROP TABLE IF EXISTS alembic_version;")) 
    conn.commit()

print("✅ Database wiped clean (including Alembic history).")