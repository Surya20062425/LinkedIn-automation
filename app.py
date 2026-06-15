import streamlit as st
import pandas as pd
import sqlite3
import asyncio
from database import DB_NAME, init_db, add_new_target, transition_to_accepted
from worker import process_outbound_queue

st.set_page_config(page_title="Executive Outreach Hub", layout="wide")
init_db()

# Custom header styling
st.markdown("## 📈 Enterprise Outbound Growth Deck")
st.write("Cross-channel LinkedIn Network Sync & Transactional Mail Gateway Engine.")
st.markdown("---")

# Data Synchronization Layer
def get_pipeline_dataframe():
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query("SELECT * FROM outbound_pipeline ORDER BY detected_at DESC", conn)

df = get_pipeline_dataframe()

# Top-Tier KPI Metrics Row
if not df.empty:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Prospects Sourced", len(df))
    m2.metric("Awaiting Acceptances", len(df[df['status'] == 'SENT_CONNECTION_REQUEST']))
    m3.metric("Emails Successfully Sent", len(df[df['status'] == 'EMAIL_SENT']))
    m4.metric("Failed Routing Steps", len(df[df['status'].isin(['EMAIL_NOT_FOUND', 'DELIVERY_FAILED'])]))
    
    st.markdown("### 🛠️ Live Target Action Registry")
    
    # Render active action items
    for idx, row in df.iterrows():
        if row['status'] == 'SENT_CONNECTION_REQUEST':
            col_info, col_trigger = st.columns([4, 1])
            col_info.write(f"🔹 **{row['first_name']} {row['last_name']}** — {row['company_name']} ({row['industry_vertical']})")
            if col_trigger.button("Simulate LinkedIn Acceptance", key=f"btn_{row['id']}"):
                transition_to_accepted(row['linkedin_url'])
                st.rerun()
                
    st.markdown("### 📊 Operational Master Logs")
    st.dataframe(df, use_container_width=True)
else:
    st.info("System operational queue is currently empty. Inject records via the sidebar sandbox to execute loops.")

# Sidebar Data Ingestion Control Panel
st.sidebar.header("📥 Database Manual Lead Injection")
with st.sidebar.form("lead_form"):
    f_name = st.text_input("First Name", "Jane")
    l_name = st.text_input("Last Name", "Smith")
    l_url = st.text_input("LinkedIn Profile URL", "https://linkedin.com/in/janesmith")
    c_name = st.text_input("Company Name", "Stripe")
    c_dom = st.text_input("Company Domain (for email finding)", "stripe.com")
    ind_vert = st.selectbox("Industry Vertical", ["Fintech", "SaaS", "AI/ML", "Healthcare", "General"])
    
    if st.form_submit_button("Splat Record Into Engine Pipeline"):
        if add_new_target(l_url, f_name, l_name, c_name, c_dom, ind_vert):
            st.sidebar.success(f"Tracked lead: {f_name} {l_name}")
            st.rerun()
        else:
            st.sidebar.error("LinkedIn URL validation footprint match already indexed.")

# Integrated Background Worker Toggle Switch
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Core Processing Systems")
if st.sidebar.checkbox("Activate Async Background Mail Worker"):
    st.sidebar.warning("Worker thread running safely in background...")
    # Fire off async loops safely via streamlit run bounds
    try:
        loop = asyncio.get_event_loop()
        if not loop.is_running():
            loop.run_until_complete(process_outbound_queue())
        else:
            asyncio.ensure_future(process_outbound_queue())
    except Exception:
        pass
