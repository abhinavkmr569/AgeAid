import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "")

# 1. Fix Driver Prefix for CockroachDB
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "cockroachdb://", 1)

# 2. SSL Certificate Handling
# Docker Strategy: We rely on the Dockerfile placing the cert in /root/.postgresql/root.crt
# Windows Strategy: We manually point to AppData

win_cert_path = os.path.join(os.environ.get("APPDATA", ""), "postgresql", "root.crt")
operator = "&" if "?" in DATABASE_URL else "?"

if sys.platform == "win32" and os.path.exists(win_cert_path):
    # Only modify URL for Windows
    if "sslrootcert" not in DATABASE_URL:
        DATABASE_URL += f"{operator}sslrootcert={win_cert_path}"
        print(f"🔒 Using Windows SSL Cert: {win_cert_path}")
else:
    # On Linux/Docker, do NOT append sslrootcert.
    # The driver will automatically check ~/.postgresql/root.crt which we populated.
    print("🔒 Using System Default SSL Cert Path (Docker)")

# 3. Create Engine
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    print(f"❌ CRITICAL DB ERROR: {e}")
    raise e

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()