from dateutil import parser
from datetime import datetime

def standardize_date(date_str):
    """
    Ensures date is saved as YYYY-MM-DD.
    Prioritizes DD/MM/YYYY format (India/UK).
    """
    if not date_str: return None
    
    clean_date = str(date_str).strip()
    
    # 1. Try strict DD/MM/YYYY first
    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d %B %Y", "%d %b %Y"]:
        try:
            dt = datetime.strptime(clean_date, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # 2. Fallback to intelligent parser with dayfirst=True
    try:
        dt = parser.parse(clean_date, dayfirst=True)
        return dt.strftime("%Y-%m-%d")
    except:
        return None

def format_date_ui(iso_date_str):
    """
    Converts YYYY-MM-DD -> 01 Nov 2025
    """
    if not iso_date_str: return "Unknown"
    try:
        dt = datetime.strptime(iso_date_str, "%Y-%m-%d")
        return dt.strftime("%d %b %Y") 
    except:
        return iso_date_str