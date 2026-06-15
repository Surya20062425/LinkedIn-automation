import streamlit as st
import pandas as pd
import sqlite3
import asyncio
from database import DB_NAME, init_db, add_new_target, transition_to_accepted
from worker import process_outbound_queue

st.set_page_config(page_title="Executive Outreach Hub", layout="wide")
init_db()

# --- NEW: Cloud Optimizations ---
# 1. Access keys from Streamlit's cloud secrets safely
HUNTER_API_KEY = st.secrets["HUNTER_API_KEY"]
EMAIL_SENDER = st.secrets["COMPANY_EMAIL"]

# 2. Fire an instant, non-blocking check every time the page renders 
async def run_pipeline_tick():
    try:
        # Import and trigger the task processing unit logic safely
        from worker import process_outbound_queue_once
        await process_outbound_queue_once()
    except Exception as e:
        pass

# Schedule the asynchronous execution immediately as the app runs top-to-bottom
asyncio.run(run_pipeline_tick())
# ---------------------------------

st.markdown("## 📈 Enterprise Outbound Growth Deck")
st.write("Cross-channel LinkedIn Network Sync & Transactional Mail Gateway Engine.")
st.markdown("---")

# Rest of your dashboard code stays exactly the same...
