import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# 1. Parse URL
DATABASE_URL = os.environ.get("DATABASE_URL", "")
"""if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "cockroachdb://", 1)"""

# 2. Windows SSL Fix (Same as database.py)
if sys.platform == "win32" and "sslrootcert" not in DATABASE_URL:
    appdata = os.environ.get("APPDATA")
    if appdata:
        cert_path = os.path.join(appdata, "postgresql", "root.crt")
        DATABASE_URL += f"&sslrootcert={cert_path}"

# 3. Connect
engine = create_engine(DATABASE_URL)

print("------ DIAGNOSTICS ------")
try:
    with engine.connect() as conn:
        # A. Check which Database we are actually inside
        db_name = conn.execute(text("SELECT current_database()")).scalar()
        print(f"📂 Connected to Database: '{db_name}'")
        
        # B. List all tables (To see if 'users' actually exists here)
        print("📋 Tables found in this DB:")
        tables = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")).fetchall()
        for t in tables:
            print(f"   - {t[0]}")

        # C. Check Users
        print("\n🔍 Checking 'users' table...")
        if any(t[0] == 'users' for t in tables):
            result = conn.execute(text("SELECT id, email, full_name FROM users"))
            users = result.fetchall()
            
            if not users:
                print("❌ Table 'users' exists but is EMPTY.")
            else:
                print(f"✅ Found {len(users)} user(s):")
                for user in users:
                    print(f"   [ID: {user.id}] {user.email} ({user.full_name})")
        else:
            print("❌ ERROR: Table 'users' does NOT exist in this database.")

except Exception as e:
    print(f"❌ Connection Error: {e}")
print("-------------------------")


# **Run it locally:**
#bash

# python check_users.py

# *(Note: Check if the output says `Connected to Database: 'healthdb'`. If it says `defaultdb`, your `.env` file is wrong).*



### 🛠️ Step 2: The "Debug Endpoint" (The Surefire Way)
# Since your App is running inside Docker, the most reliable way to check data is to ask the App itself.

# Add this temporary endpoint to your **`main.py`** file (just before the `if __name__ == "__main__":` line).

#python
"""@app.get("/debug/users")
def debug_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {
        "count": len(users),
        "database_url_masked": str(engine.url).split("@")[-1], # Shows host/db only
        "users": [{"id": u.id, "email": u.email} for u in users]
    }"""

"""
**Rebuild and Run:**
bash
docker rm -f health-server
docker build -t health-app .
docker run -d --name health-server -p 8080:8080 -p 8501:8501 --env-file .env -v $env:APPDATA\postgresql:/root/.postgresql health-app


**Check in Browser:**
Go to: `http://localhost:8080/debug/users`

* **If this returns users:** Your app is working perfectly, and your local `check_users.py` script was just looking at the wrong DB.
* **If this returns empty:** The signup process is silently failing.



### 🚨 Step 3: If Signup is failing silently...
It is possible the browser is saying "Success" but the database transaction is rolling back.
Check your **Docker Logs** immediately after signing up:

-> bash

docker logs health-server

"""