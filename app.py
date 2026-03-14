import streamlit as st
import requests
import pandas as pd
import altair as alt
import time
import os
from datetime import datetime, date
from requests.exceptions import ConnectionError
from utils import format_date_ui
from dotenv import load_dotenv

load_dotenv()

try: from clusters import TEST_CLUSTERS
except: TEST_CLUSTERS = {}

# 1. CONFIGURATION (Must be first)
st.set_page_config(page_title="Health AI", layout="wide", initial_sidebar_state="expanded")

# --- SMART URL CONFIGURATION ---
# Internal URL: Server-to-Server (Streamlit -> FastAPI inside Docker)
API_URL = "http://127.0.0.1:8502"

# External URL: Browser Redirects (Google Login)



# LOGIC: Check .env first, fallback to localhost.
PUBLIC_API_URL = os.environ.get("PUBLIC_API_URL", "http://localhost:8080")

# Remove trailing slash if present to avoid double // issues
if PUBLIC_API_URL.endswith("/"):
    PUBLIC_API_URL = PUBLIC_API_URL[:-1]

# -------------------------------

# 2. SESSION STATE INITIALIZATION
if 'user_id' not in st.session_state: st.session_state['user_id'] = None
if 'user_name' not in st.session_state: st.session_state['user_name'] = None
if 'page' not in st.session_state: st.session_state['page'] = 'Landing' 
if 'selected_test' not in st.session_state: st.session_state['selected_test'] = None
if 'current_remarks' not in st.session_state: st.session_state['current_remarks'] = ""
if 'trend_raw' not in st.session_state: st.session_state['trend_raw'] = {}
if 'health_logs' not in st.session_state: st.session_state['health_logs'] = []
if 'trend_analysis' not in st.session_state: st.session_state['trend_analysis'] = None
if 'last_t' not in st.session_state: st.session_state['last_t'] = None

# --- AUTH SESSION HANDLER ---
try:
    query_params = st.query_params
    # FIX: Add check 'and st.session_state['user_id'] is None' to prevent infinite rerun loops
    if query_params.get("login_success") == "true" and st.session_state['user_id'] is None:
        st.session_state['user_id'] = query_params.get("uid")
        st.session_state['user_name'] = query_params.get("uname")
        st.session_state['page'] = 'App'
        
        # Clear params to clean up URL
        st.query_params.clear()
        
        st.success(f"Welcome back, {st.session_state['user_name']}!")
        time.sleep(1)
        st.rerun()
        
    elif query_params.get("login_error"):
        st.error(f"Google Login Failed: {query_params.get('login_error')}")
except: pass

# --- HELPERS ---

def safe_api_call(method, endpoint, **kwargs):
    """Robust API caller"""
    url = f"{API_URL}{endpoint}"
    for attempt in range(3):
        try:
            if method == "POST": res = requests.post(url, **kwargs)
            elif method == "PUT": res = requests.put(url, **kwargs)
            elif method == "DELETE": res = requests.delete(url, **kwargs)
            else: res = requests.get(url, **kwargs)
            
            if res.status_code in [500, 502, 503, 504]: 
                time.sleep(1); continue
            return res
        except ConnectionError:
            time.sleep(1); continue
            
    return requests.Response()

def get_health_status(value, min_ref, max_ref):
    if value is None or value == -1: return (None, "#808080", "Info")
    try:
        val = float(value)
        mn = float(min_ref) if min_ref is not None else 0.0
        mx = float(max_ref) if max_ref is not None else float('inf')
    except: return (None, "#808080", "Error")

    if mn == 0.0 and mx != float('inf'): # < 200
        if val <= mx: return (25 + (val/mx)*50, "#2ECC71", "Normal")
        else: return (min(100, 75 + (val-mx)*10), "#E74C3C", "High")
    if mn != 0.0 and mx == float('inf'): # > 55
        if val >= mn: return (50, "#2ECC71", "Normal")
        else: return (15, "#E74C3C", "Low")
    try:
        if mx == float('inf'): return (50, "#2ECC71", "Normal")
        range_span = mx - mn
        if range_span == 0: return (50, "#2ECC71", "Normal")
        pos = (val - mn) / range_span
        score = max(0, min(100, 25 + (pos * 50)))
        if 25 <= score <= 75: return (score, "#2ECC71", "Normal")
        elif 15 <= score < 25 or 75 < score <= 85: return (score, "#F1C40F", "Borderline")
        else: return (score, "#E74C3C", "Abnormal")
    except: return (None, "#808080", "Error")

# --- VIEWS ---

def render_landing_page():
    st.markdown("""
    <div style='text-align: center; padding: 50px 0;'>
        <h1>🩺 Health Trend Tracker</h1>
        <h3>Your Personal AI Health Assistant</h3>
        <p style='font-size: 18px; color: #666;'>
            Upload your blood reports, visualize trends, and get personalized insights powered by Gemini AI.
            <br>Secure. Private. Intelligent.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("🚀 Get Started / Login", type="primary", use_container_width=True):
            st.session_state['page'] = 'Login'
            st.rerun()
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.info("📊 **Visualize Trends**\n\nSee how your cholesterol or sugar levels change over time.")
    c2.success("🤖 **AI Insights**\n\nGet actionable advice based on your lifestyle and report data.")
    c3.warning("🔒 **Privacy First**\n\nYour data is yours. Delete your account anytime.")

def render_account_settings():
    st.header("👤 Account Settings")
    st.info("Manage your profile preferences and data.")
    try:
        res = safe_api_call("GET", f"/user/{st.session_state['user_id']}/profile")
        if res.status_code == 200: profile = res.json().get('profile', {})
        else: st.error("Failed to load profile"); return
    except: return

    with st.form("edit_profile"):
        st.subheader("Lifestyle & Preferences")
        c1, c2 = st.columns(2)
        d_opts = ["Omnivore", "Veg", "Vegan", "Keto"]
        curr_d = profile.get('diet_type', 'Omnivore')
        d = c1.selectbox("Diet Type", d_opts, index=d_opts.index(curr_d) if curr_d in d_opts else 0)
        
        act_help = "Sedentary: Little/no exercise\nModerate: Exercise 1-3 times/week\nActive: Daily exercise or physical job"
        a = c2.select_slider("Activity Level", options=["Sedentary", "Moderate", "Active"], 
                             value=profile.get('activity_level', 'Moderate'), help=act_help)
        
        c3, c4 = st.columns(2)
        s_opts = ["Never", "Former", "Current"]
        curr_s = profile.get('smoking_status', 'Never')
        smoke = c3.radio("Smoking", s_opts, horizontal=True, index=s_opts.index(curr_s) if curr_s in s_opts else 0)
        
        al_opts = ["None", "Social", "Moderate", "Frequent"]
        curr_al = profile.get('alcohol_freq', 'None')
        alcohol = c4.selectbox("Alcohol", al_opts, index=al_opts.index(curr_al) if curr_al in al_opts else 0)
        
        s = st.slider("Sleep Hours", 4.0, 12.0, float(profile.get('sleep_hours', 7.0)))
        med = st.text_area("Medical History", value=profile.get('medical_history', ''))
        
        if st.form_submit_button("💾 Save Changes"):
            payload = {"diet_type": d, "activity_level": a, "smoking_status": smoke, "alcohol_freq": alcohol, "sleep_hours": s, "medical_history": med}
            res = safe_api_call("PUT", f"/user/{st.session_state['user_id']}/update_profile", json=payload)
            if res.status_code == 200: st.success("Profile Updated!"); time.sleep(1); st.rerun()
            else: st.error("Failed to update.")

    st.divider()
    st.subheader("🚨 Danger Zone")
    if st.button("🗑️ Delete My Account Permanently", type="primary"):
        st.warning("Are you sure? This cannot be undone.")
        if st.button("Yes, I am sure. Delete everything."):
            res = safe_api_call("DELETE", f"/user/{st.session_state['user_id']}/delete")
            if res.status_code == 200: st.session_state.clear(); st.success("Account Deleted."); time.sleep(2); st.rerun()
            else: st.error("Failed to delete account.")

def login():
    st.button("← Back to Home", on_click=lambda: st.session_state.update({'page': 'Landing'}))
    st.header("🔑 Login")
    
    # --- GOOGLE LOGIN BUTTON ---
    # FIXED: Uses clean PUBLIC_API_URL from .env
    st.markdown(f'''
    <a href="{PUBLIC_API_URL}/auth/login" target="_self" style="text-decoration: none;">
        <div style="
            width: 100%; background-color: #fff; border: 1px solid #ccc;
            padding: 10px; border-radius: 5px; text-align: center;
            display: flex; align-items: center; justify_content: center; gap: 10px;
            cursor: pointer; font-family: sans-serif; color: #333">
            <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" width="18">
            <span style="font-weight: 500;">Sign in with Google</span>
        </div>
    </a>
    <br> ''', unsafe_allow_html=True)
    
    st.markdown("<div style='text-align: center; color: #666;'>— OR —</div>", unsafe_allow_html=True)
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Log In", type="primary"):
        try:
            res = safe_api_call("POST", "/login", json={"email": email, "password": password})
            if res.status_code == 200:
                d = res.json()
                st.session_state.update({'user_id': d['user_id'], 'user_name': d['name'], 'page': 'App'})
                st.rerun()
            elif res.status_code == 422: st.error("Invalid data format")
            else: st.error("Invalid Credentials")
        except ConnectionError: st.error("Backend is still starting up. Please wait 5 seconds and try again.")
        except Exception as e: st.error(f"An error occurred: {e}")
    
    st.markdown("---")
    st.caption("New here?")
    if st.button("Create an Account"): st.session_state['page'] = 'Signup'; st.rerun()

def signup():
    st.button("← Back to Login", on_click=lambda: st.session_state.update({'page': 'Login'}))
    st.header("📝 Create Profile")
    with st.form("s"):
        c1,c2 = st.columns(2)
        email = c1.text_input("Email")
        password = c2.text_input("Password", type="password")
        name = st.text_input("Name")
        dob = st.date_input("DOB", min_value=date(1940,1,1))
        gender = st.selectbox("Gender", ["Male", "Female"])
        st.divider()
        st.subheader("Lifestyle")
        d = st.selectbox("Diet", ["Omnivore", "Veg", "Vegan", "Keto"])
        act_help = "Sedentary: Little/no exercise\nModerate: Exercise 1-3 times/week\nActive: Daily exercise or physical job"
        a = st.select_slider("Activity", options=["Sedentary", "Moderate", "Active"], help=act_help)
        l1, l2 = st.columns(2)
        smoke = l1.radio("Smoking", ["Never", "Former", "Current"], horizontal=True)
        alcohol = l2.selectbox("Alcohol", ["None", "Social", "Moderate", "Frequent"])
        s = st.slider("Sleep", 4.0, 12.0, 7.0)
        med = st.text_area("Medical History")
        ai = st.checkbox("I consent to AI processing.", value=True)
        if st.form_submit_button("Sign Up", type="primary"):
            payload = {"email": email, "password": password, "full_name": name, "dob": str(dob), "gender": gender, "medical_history": med, "activity_level": a, "diet_type": d, "alcohol_freq": alcohol, "smoking_status": smoke, "sleep_hours": s, "ai_consent": ai}
            try:
                res = safe_api_call("POST", "/signup", json=payload)
                if res.status_code == 200:
                    st.success("Done! Login.")
                    st.session_state['page'] = 'Login'
                    st.rerun()
                elif res.status_code == 422:
                    errors = res.json().get("detail", [])
                    if isinstance(errors, list):
                        error_msg = "\n".join([f"• {e['loc'][-1]}: {e['msg']}" for e in errors])
                        st.error(f"⚠️ Please fix the following:\n{error_msg}")
                    else: st.error(f"Validation Error: {errors}")
                else: st.error(f"Error: {res.text}")
            except Exception as e: st.error(f"Connection Failed: {e}")

# --- DASHBOARD ---
def render_home():
    st.title(f"👋 Hi, {st.session_state.get('user_name')}")
    if not st.session_state['health_logs']:
        try:
            r = safe_api_call("GET", f"/user/{st.session_state['user_id']}/profile")
            if r.status_code == 200: st.session_state['health_logs'] = r.json().get('logs', [])
        except: pass

    with st.container():
        st.subheader("📝 Health Journal")
        if st.session_state['health_logs']:
            with st.expander("View History", expanded=False):
                for log in reversed(st.session_state['health_logs']):
                    st.markdown(f"**`{log.get('timestamp','?')}`** {log.get('content')}")
        
        with st.form("add_log", clear_on_submit=True):
            new_rem = st.text_area("Add Entry:", height=70, placeholder="e.g. Started gym today")
            if st.form_submit_button("Add"):
                safe_api_call("POST", f"/user/{st.session_state['user_id']}/update_remarks", json={"remarks": new_rem})
                ts = datetime.now().strftime("%Y-%m-%d %H:%Mhrs")
                st.session_state['health_logs'].append({"timestamp": ts, "content": new_rem})
                st.session_state['current_remarks'] = new_rem
                st.rerun()

    st.divider()

    with st.expander("📤 Upload Reports", expanded=True):
            ups = st.file_uploader("Files", type=["pdf","jpg","png"], accept_multiple_files=True)
            if ups and st.button(f"Process {len(ups)} Files"):
                status_text = st.empty()
                progress_bar = st.progress(0)
                total_files = len(ups)
                for i, f in enumerate(ups):
                    status_text.markdown(f"**⏳ Processing ({i+1}/{total_files}) reports:** `{f.name}`...")
                    try:
                        safe_api_call("POST", "/analyze", files={"file": (f.name, f.getvalue(), f.type)}, data={"user_id": st.session_state['user_id']})
                    except Exception as e: st.error(f"Failed to process {f.name}")
                    progress_bar.progress((i + 1) / total_files)
                
                status_text.success(f"✅ Done! Processed {total_files} reports.")
                time.sleep(1.5)
                st.rerun()

    st.sidebar.header("📜 Report History")
    res_hist = safe_api_call("GET", f"/user/{st.session_state['user_id']}/history")
    try:
        hist = res_hist.json().get("reports", [])
        report_map = {format_date_ui(h['date']): h['id'] for h in hist}
        selected_report_id = None
        if report_map:
            sel_date = st.sidebar.radio("Select:", list(report_map.keys()))
            selected_report_id = report_map[sel_date]
        else: st.sidebar.info("No reports.")
    except: st.sidebar.warning("Syncing...")
    
    st.sidebar.divider()
    if st.sidebar.button("👤 Account Settings"): st.session_state['page'] = 'Settings'; st.rerun()
    if st.sidebar.button("Logout"): st.session_state.clear(); st.rerun()

    if selected_report_id:
        res_rep = safe_api_call("GET", f"/report/{selected_report_id}")
        if res_rep.status_code == 200:
            d = res_rep.json()
            st.subheader(f"📋 {format_date_ui(d['report_date'])} | {d.get('lab', 'Unknown Lab')}")
            for i, r in enumerate(d.get("results", [])):
                score, color, status = get_health_status(r['value'], r.get('min_ref'), r.get('max_ref'))
                with st.container():
                    c1, c2, c3, c4 = st.columns([2.5, 1, 0.8, 3])
                    if c1.button(f"🔗 {r['test_name']}", key=f"btn_{i}"):
                        st.session_state.update({'selected_test': r['test_name'], 'page': 'Trend'})
                        st.rerun()
                    c1.caption(f"Ref: {r.get('min_ref','?')}-{r.get('max_ref','?')}")
                    c2.write(f"**{r['value']}**")
                    c3.caption(r['unit'])
                    if score: 
                        c4.progress(int(score))
                        c4.markdown(f"<span style='color:{color}'>● {status}</span>", unsafe_allow_html=True)
                    st.write("---")
        else: st.error("Loading report...")
    else: st.info("Select a report.")

def render_analysis():
    st.header("🤖 System Analysis")
    if TEST_CLUSTERS:
        cluster = st.selectbox("Select System:", list(TEST_CLUSTERS.keys()))
        if st.button(f"Analyze {cluster}"):
            with st.spinner("Consulting AI..."):
                context = st.session_state.get('current_remarks', '')
                res = safe_api_call("POST", "/analyze_trend", data={"user_id": st.session_state['user_id'], "test_name": cluster, "remarks": context})
                if res.status_code == 200: st.markdown(res.json().get('analysis')); st.warning("AI Generated.")
                else: st.error("Failed to generate analysis.")

def render_history():
    st.header("📜 Full History")
    try:
        res = safe_api_call("GET", f"/user/{st.session_state['user_id']}/all_tests")
        if res.status_code == 200:
            raw_data = res.json().get("data", [])
            df = pd.DataFrame(raw_data)
            if not df.empty:
                df['Date'] = df['Date'].apply(format_date_ui)
                display_cols = ["Date", "Test Name", "Value", "Unit", "Reference", "Lab"]
                cols_to_show = [c for c in display_cols if c in df.columns]
                st.dataframe(df[cols_to_show], width="stretch", hide_index=True)
            else: st.info("No records.")
    except Exception as e: st.error(f"Error loading history: {e}")

def show_trend():
    if st.button("← Back"): st.session_state['page'] = 'App'; st.rerun()
    test = st.session_state['selected_test']
    st.title(f"📈 {test}")
    
    with st.spinner("Analyzing Trend..."):
        if 'trend_raw' not in st.session_state or st.session_state.get('last_t') != test:
            res = safe_api_call("POST", "/analyze_trend", data={"user_id": st.session_state['user_id'], "test_name": test})
            if res.status_code == 200:
                st.session_state['trend_raw'] = res.json()
                st.session_state['last_t'] = test
                st.session_state['trend_analysis'] = None
            else: st.error(f"Could not load trend. (Status: {res.status_code})"); return
            
        hist = st.session_state['trend_raw'].get('history', [])
        if hist:
            dates = [datetime.strptime(h['date'], "%Y-%m-%d").date() for h in hist]
            if len(dates) > 1:
                s_range = st.slider("Timeline:", min(dates), max(dates), (min(dates), max(dates)), format="DD/MM/YYYY")
                filtered_hist = [h for h in hist if s_range[0] <= datetime.strptime(h['date'], "%Y-%m-%d").date() <= s_range[1]]
            else:
                s_range = (dates[0], dates[0]) if dates else (None, None)
                filtered_hist = hist

            with st.expander("Data Table"):
                df = pd.DataFrame(filtered_hist)
                df['Date'] = df['date'].apply(format_date_ui)
                st.dataframe(df[['Date', 'value', 'unit', 'min_ref', 'max_ref', 'lab']], width="stretch")

            with st.expander("Trend Graph", expanded=True):
                chart_data = []
                for h in filtered_hist:
                    score, _, _ = get_health_status(h['value'], h['min_ref'], h['max_ref'])
                    if score: chart_data.append({"Date": format_date_ui(h['date']), "SortDate": h['date'], "Score": int(score), "Value": h['value'], "Unit": h['unit']})
                
                if chart_data:
                    df_c = pd.DataFrame(chart_data).sort_values(by="SortDate")
                    mode = st.radio("Mode:", ["Universal Score", "Absolute Value"], horizontal=True)
                    if "Universal" in mode: y_f, y_s, c, fmt = ("Score", alt.Scale(domain=[0, 100]), "#2ECC71", "d") 
                    else: y_f, y_s, c, fmt = ("Value", alt.Scale(zero=False, padding=20), "#3498DB", ".1f")
                    
                    base = alt.Chart(df_c).encode(x=alt.X('Date', sort=df_c['SortDate'].tolist()), tooltip=['Date', 'Value', 'Score'])
                    line = base.mark_line(color=c).encode(y=alt.Y(y_f, scale=y_s))
                    points = base.mark_circle(size=100, color='white', stroke=c, strokeWidth=2).encode(y=y_f)
                    text = base.mark_text(dy=-15, color='white').encode(y=y_f, text=alt.Text(y_f, format=fmt))
                    st.altair_chart((line + points + text).interactive(), use_container_width=True)

            if st.button("Analyze Period"):
                 with st.spinner("Thinking..."):
                      start = str(s_range[0]) if len(dates)>1 else None
                      end = str(s_range[1]) if len(dates)>1 else None
                      res = safe_api_call("POST", "/analyze_trend", data={
                          "user_id": st.session_state['user_id'], 
                          "test_name": test, 
                          "remarks": st.session_state.get('current_remarks', ''),
                          "start_date": start, "end_date": end
                      })
                      st.session_state['trend_analysis'] = res.json().get('analysis')
            
            with st.expander("🤖 AI Analysis", expanded=True):
                if st.session_state.get('trend_analysis'): st.markdown(st.session_state['trend_analysis'])
                else: st.markdown(st.session_state['trend_raw'].get('analysis', 'Click "Analyze Period" to generate detailed insights.'))
        else: st.info("No history.")

# --- ROUTER ---
if st.session_state['user_id'] is None:
    if st.session_state['page'] == 'Login': login()
    elif st.session_state['page'] == 'Signup': signup()
    else: render_landing_page()
else:
    if st.session_state['page'] == 'App': 
        t1, t2, t3 = st.tabs(["Home", "Analysis", "History"])
        with t1: render_home()
        with t2: render_analysis()
        with t3: render_history()
    elif st.session_state['page'] == 'Trend': show_trend()
    elif st.session_state['page'] == 'Settings': 
        if st.button("← Back"): st.session_state['page'] = 'App'; st.rerun()
        render_account_settings()