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

# --- CONFIGURATION ---
TARGET_EMAIL = "dub@gmail.com"  # <--- REPLACE THIS WITH THE ACTUAL EMAIL
# ---------------------

print(f"🧹 Cleaning Report Data for user: {TARGET_EMAIL}...")

with engine.connect() as conn:
    try:
        # A. Find the User ID
        result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": TARGET_EMAIL}).fetchone()
        
        if not result:
            print(f"❌ User '{TARGET_EMAIL}' not found.")
        else:
            user_id = result[0]
            print(f"🔍 Found User ID: {user_id}")

            # B. Delete Test Results (Child table) linked to this user's reports
            # We use a subquery to find report_ids belonging to this user
            delete_results_query = text("""
                DELETE FROM test_results 
                WHERE report_id IN (
                    SELECT id FROM patient_reports WHERE user_id = :uid
                )
            """)
            r1 = conn.execute(delete_results_query, {"uid": user_id})
            print(f"✅ Deleted {r1.rowcount} test result rows.")

            # C. Delete Reports (Parent table) for this user
            delete_reports_query = text("DELETE FROM patient_reports WHERE user_id = :uid")
            r2 = conn.execute(delete_reports_query, {"uid": user_id})
            print(f"✅ Deleted {r2.rowcount} report rows.")
            
            conn.commit()
            print(f"✨ Successfully wiped medical data for {TARGET_EMAIL}.")

    except Exception as e:
        print(f"❌ Error: {e}")

"""
How to run:
1. docker cp clear_reports.py health-server:/app/clear_reports.py
2. docker exec health-server python clear_reports.py
"""