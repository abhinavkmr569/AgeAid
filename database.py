import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "")

# 1. Fix Driver Prefix
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "cockroachdb://", 1)

# 2. SSL Certificate Handling (Windows Fix)
if sys.platform == "win32" and "sslrootcert" not in DATABASE_URL:
    appdata = os.environ.get("APPDATA")
    if appdata:
        cert_path = os.path.join(appdata, "postgresql", "root.crt")
        if os.path.exists(cert_path):
            DATABASE_URL += f"&sslrootcert={cert_path}"

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