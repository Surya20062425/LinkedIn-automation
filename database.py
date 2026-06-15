import sqlite3
from datetime import datetime, timedelta

DB_NAME = "enterprise_outreach.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outbound_pipeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                linkedin_url TEXT UNIQUE,
                first_name TEXT NOT None,
                last_name TEXT NOT None,
                company_name TEXT NOT None,
                company_domain TEXT NOT None,
                industry_vertical TEXT DEFAULT 'General',
                status TEXT DEFAULT 'SENT_CONNECTION_REQUEST',
                detected_at TIMESTAMP NOT None,
                accepted_at TIMESTAMP,
                scheduled_email_at TIMESTAMP,
                processed_at TIMESTAMP,
                resolved_email TEXT
            )
        """)
        conn.commit()

def add_new_target(linkedin_url, first_name, last_name, company, domain, vertical):
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO outbound_pipeline (linkedin_url, first_name, last_name, company_name, company_domain, industry_vertical, detected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (linkedin_url, first_name, last_name, company, domain, vertical, datetime.now()))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def transition_to_accepted(linkedin_url, delay_hours=1):
    """Triggers when a connection acceptance is confirmed. Sets a safety delay."""
    accepted_time = datetime.now()
    scheduled_time = accepted_time + timedelta(hours=delay_hours)
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE outbound_pipeline 
            SET status = 'CONNECTION_ACCEPTED', accepted_at = ?, scheduled_email_at = ?
            WHERE linkedin_url = ? AND status = 'SENT_CONNECTION_REQUEST'
        """, (accepted_time, scheduled_time, linkedin_url))
        conn.commit()
