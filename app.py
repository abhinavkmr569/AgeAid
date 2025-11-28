import streamlit as st
import requests
import pandas as pd
import altair as alt
from datetime import datetime, date
from utils import format_date_ui
try: from clusters import TEST_CLUSTERS
except: TEST_CLUSTERS = {}

# 1. CONFIGURATION (Must be first)
st.set_page_config(page_title="Health AI", layout="wide", initial_sidebar_state="expanded")
API_URL = "http://127.0.0.1:8080"

# 2. SESSION STATE INITIALIZATION (CRITICAL: Must be at the top)
# This block ensures keys exist before any logic tries to access them.
if 'user_id' not in st.session_state: st.session_state['user_id'] = None
if 'user_name' not in st.session_state: st.session_state['user_name'] = None
if 'page' not in st.session_state: st.session_state['page'] = 'Login'
if 'selected_test' not in st.session_state: st.session_state['selected_test'] = None
if 'current_remarks' not in st.session_state: st.session_state['current_remarks'] = ""
if 'trend_raw' not in st.session_state: st.session_state['trend_raw'] = {}
if 'health_logs' not in st.session_state: st.session_state['health_logs'] = []
if 'trend_analysis' not in st.session_state: st.session_state['trend_analysis'] = None  # Fix for analysis persistence
if 'last_t' not in st.session_state: st.session_state['last_t'] = None # Fix for trend data caching

# --- HELPER: HEALTH STATUS ---

def calculate_cost(model_name, tokens):
    if not tokens or not model_name: return 0.0
    # Approx Pricing ($ per 1M tokens)
    rates = {"gemini-2.5-flash": 0.10, "gemini-2.5-pro": 2.50}
    rate = rates.get(model_name, 0.10)
    return (tokens / 1_000_000) * rate

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

# --- AUTH VIEWS ---
def login():
    st.header("🔑 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Log In", type="primary"):
        try:
            res = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
            if res.status_code == 200:
                d = res.json()
                st.session_state.update({'user_id': d['user_id'], 'user_name': d['name'], 'page': 'App'})
                st.rerun()
            else: st.error("Invalid Credentials")
        except: st.error("Backend offline")

def signup():
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
        a = st.select_slider("Activity", options=["Sedentary", "Moderate", "Active"])
        l1, l2 = st.columns(2)
        smoke = l1.radio("Smoking", ["Never", "Former", "Current"], horizontal=True)
        alcohol = l2.selectbox("Alcohol", ["None", "Social", "Moderate", "Frequent"])
        s = st.slider("Sleep", 4.0, 12.0, 7.0)
        med = st.text_area("Medical History")
        ai = st.checkbox("I consent to AI processing.", value=True)
        if st.form_submit_button("Sign Up", type="primary"):
            payload = {"email": email, "password": password, "full_name": name, "dob": str(dob), "gender": gender, "medical_history": med, "activity_level": a, "diet_type": d, "alcohol_freq": alcohol, "smoking_status": smoke, "sleep_hours": s, "ai_consent": ai}
            res = requests.post(f"{API_URL}/signup", json=payload)
            if res.status_code == 200: st.success("Done! Login."); st.session_state['page']='Login'; st.rerun()
            else: st.error(res.text)

# --- DASHBOARD ---
def render_home():
    st.title(f"👋 Hi, {st.session_state.get('user_name')}")
    
    # Fetch Logs
    if not st.session_state['health_logs']:
        try:
            r = requests.get(f"{API_URL}/user/{st.session_state['user_id']}/profile").json()
            st.session_state['health_logs'] = r.get('logs', [])
        except: pass

    # Remarks UI (Timeline Style)
    with st.container():
        st.subheader("📝 Health Journal")
        if st.session_state['health_logs']:
            with st.expander("View History", expanded=False):
                for log in reversed(st.session_state['health_logs']):
                    st.markdown(f"**`{log.get('timestamp','?')}`** {log.get('content')}")
        
        with st.form("add_log", clear_on_submit=True):
            new_rem = st.text_area("Add Entry:", height=70, placeholder="e.g. Started gym today")
            if st.form_submit_button("Add"):
                requests.post(f"{API_URL}/user/{st.session_state['user_id']}/update_remarks", json={"remarks": new_rem})
                # Optimistic Update
                ts = datetime.now().strftime("%Y-%m-%d %H:%Mhrs")
                st.session_state['health_logs'].append({"timestamp": ts, "content": new_rem})
                st.session_state['current_remarks'] = new_rem # Keep latest as context
                st.rerun()

    st.divider()

    # Upload
    with st.expander("📤 Upload Reports", expanded=True):
        ups = st.file_uploader("Files", type=["pdf","jpg","png"], accept_multiple_files=True)
        if ups and st.button(f"Process {len(ups)}"):
            p = st.progress(0)
            for i, f in enumerate(ups):
                try: requests.post(f"{API_URL}/analyze", files={"file": (f.name, f.getvalue(), f.type)}, data={"user_id": st.session_state['user_id']})
                except: pass
                p.progress((i+1)/len(ups))
            st.success("Done!"); st.rerun()

    # Sidebar History
    st.sidebar.header("📜 Report History")
    try:
        hist = requests.get(f"{API_URL}/user/{st.session_state['user_id']}/history").json().get("reports", [])
        report_map = {format_date_ui(h['date']): h['id'] for h in hist}
        selected_report_id = None
        if report_map:
            sel_date = st.sidebar.radio("Select:", list(report_map.keys()))
            selected_report_id = report_map[sel_date]
        else: st.sidebar.info("No reports.")
    except: st.sidebar.error("Connection Error")
    
    if st.sidebar.button("Logout"): st.session_state.clear(); st.rerun()

    # Report View
    if selected_report_id:
        try:
            d = requests.get(f"{API_URL}/report/{selected_report_id}").json()
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
        except: st.error("Failed to load report")
    else: st.info("Select a report.")

def render_analysis():
    st.header("🤖 System Analysis")
    if TEST_CLUSTERS:
        cluster = st.selectbox("Select System:", list(TEST_CLUSTERS.keys()))
        if st.button(f"Analyze {cluster}"):
            with st.spinner("Consulting AI..."):
                # Use most recent remark
                context = st.session_state.get('current_remarks', '')
                res = requests.post(f"{API_URL}/analyze_trend", data={"user_id": st.session_state['user_id'], "test_name": cluster, "remarks": context})
                if res.status_code == 200: st.markdown(res.json().get('analysis')); st.warning("AI Generated.")
                else: st.error("Failed")

def render_history():
    st.header("📜 Full History")
    try:
        res = requests.get(f"{API_URL}/user/{st.session_state['user_id']}/all_tests")
        if res.status_code == 200:
            raw_data = res.json().get("data", [])
            df = pd.DataFrame(raw_data)

            if not df.empty:
                df['Date'] = df['Date'].apply(format_date_ui)

                # --- NEW LOGIC: Calculate Cost ---
                # We check if the API sent 'tokens_used' (it might be missing for old records)
                if 'tokens_used' in df.columns:
                    # 1. Calculate Cost per row
                    df['Cost ($)'] = df.apply(lambda x: calculate_cost(x.get('ai_model'), x.get('tokens_used')), axis=1)
                    
                    # 2. Show Total Metric at the top
                    total_cost = df['Cost ($)'].sum()
                    st.metric("Total AI Cost", f"${total_cost:.4f}")

                    # 3. Format the column nicely for the table (e.g. $0.00012)
                    df['Cost ($)'] = df['Cost ($)'].apply(lambda x: f"${x:.6f}")

                # Display the table
                st.dataframe(df, use_container_width=True, hide_index=True)
            else: 
                st.info("No records.")
    except Exception as e: 
        st.error(f"Error loading history: {e}")

def show_trend():
    if st.button("← Back"): st.session_state['page'] = 'App'; st.rerun()
    test = st.session_state['selected_test']
    st.title(f"📈 {test}")
    
    with st.spinner("Analyzing Trend..."):
        # Initial Fetch
        if 'trend_raw' not in st.session_state or st.session_state.get('last_t') != test:
            res = requests.post(f"{API_URL}/analyze_trend", data={"user_id": st.session_state['user_id'], "test_name": test})
            st.session_state['trend_raw'] = res.json()
            st.session_state['last_t'] = test
            st.session_state['trend_analysis'] = None # Reset analysis on new test
            
        hist = st.session_state['trend_raw'].get('history', [])
        
        if hist:
            # Date Slider Logic
            dates = [datetime.strptime(h['date'], "%Y-%m-%d").date() for h in hist]
            if len(dates) > 1:
                s_range = st.slider("Timeline:", min(dates), max(dates), (min(dates), max(dates)), format="DD/MM/YYYY")
                filtered_hist = [h for h in hist if s_range[0] <= datetime.strptime(h['date'], "%Y-%m-%d").date() <= s_range[1]]
            else:
                s_range = (dates[0], dates[0]) if dates else (None, None)
                filtered_hist = hist

            # Table
            with st.expander("Data Table"):
                df = pd.DataFrame(filtered_hist)
                df['Date'] = df['date'].apply(format_date_ui)
                st.dataframe(df[['Date', 'value', 'unit', 'min_ref', 'max_ref', 'lab']], use_container_width=True)

            # Chart
            with st.expander("Trend Graph", expanded=True):
                chart_data = []
                for h in filtered_hist:
                    score, _, _ = get_health_status(h['value'], h['min_ref'], h['max_ref'])
                    if score: chart_data.append({"Date": format_date_ui(h['date']), "SortDate": h['date'], "Score": int(score), "Value": h['value'], "Unit": h['unit']})
                
                if chart_data:
                    df_c = pd.DataFrame(chart_data).sort_values(by="SortDate")
                    mode = st.radio("Mode:", ["Universal Score", "Absolute Value"], horizontal=True)
                    if "Universal" in mode:
                        y_f, y_s, c, fmt = ("Score", alt.Scale(domain=[0, 100]), "#2ECC71", "d") 
                    else:
                        y_f, y_s, c, fmt = ("Value", alt.Scale(zero=False, padding=20), "#3498DB", ".1f")
                    
                    base = alt.Chart(df_c).encode(x=alt.X('Date', sort=df_c['SortDate'].tolist()), tooltip=['Date', 'Value', 'Score'])
                    line = base.mark_line(color=c).encode(y=alt.Y(y_f, scale=y_s))
                    points = base.mark_circle(size=100, color='white', stroke=c, strokeWidth=2).encode(y=y_f)
                    text = base.mark_text(dy=-15, color='white').encode(y=y_f, text=alt.Text(y_f, format=fmt))
                    st.altair_chart((line + points + text).interactive(), use_container_width=True)

            # Analyze specific period
            if st.button("Analyze Period"):
                 with st.spinner("Thinking..."):
                     start = str(s_range[0]) if len(dates)>1 else None
                     end = str(s_range[1]) if len(dates)>1 else None
                     res = requests.post(f"{API_URL}/analyze_trend", data={
                         "user_id": st.session_state['user_id'], 
                         "test_name": test, 
                         "remarks": st.session_state.get('current_remarks', ''),
                         "start_date": start, "end_date": end
                     })
                     st.session_state['trend_analysis'] = res.json().get('analysis')
            
            with st.expander("🤖 AI Analysis", expanded=True):
                if st.session_state.get('trend_analysis'):
                    st.markdown(st.session_state['trend_analysis'])
                else:
                    st.markdown(st.session_state['trend_raw'].get('analysis', 'Click "Analyze Period" to generate detailed insights.'))

        else:
            st.info("No history.")

# --- MAIN ROUTER ---
if st.session_state['user_id'] is None:
    if st.session_state['page'] == 'Login': login(); st.button("Sign Up", on_click=lambda: st.session_state.update({'page': 'Signup'}))
    else: signup(); st.button("Back", on_click=lambda: st.session_state.update({'page': 'Login'}))
else:
    if st.session_state['page'] == 'App': 
        t1, t2, t3 = st.tabs(["Home", "Analysis", "History"])
        with t1: render_home()
        with t2: render_analysis()
        with t3: render_history()
    elif st.session_state['page'] == 'Trend': show_trend()