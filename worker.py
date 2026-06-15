import sqlite3
from datetime import datetime
import streamlit as st
from email_engine import resolve_corporate_email, build_professional_template, execute_smtp_delivery
from database import DB_NAME

async def process_outbound_queue_once():
    """Polls database once per page render, processing time-locked targets."""
    current_time = datetime.now()
    
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM outbound_pipeline 
            WHERE status = 'CONNECTION_ACCEPTED' AND datetime(scheduled_email_at) <= datetime(?)
        """, (current_time,))
        active_jobs = cursor.fetchall()
        
        for job in active_jobs:
            # Resolve emails using Streamlit's cloud secrets configuration block
            email = resolve_corporate_email(job['first_name'], job['last_name'], job['company_domain'])
            
            if email:
                try:
                    email_body = build_professional_template(job['first_name'], job['company_name'], job['industry_vertical'])
                    subject_line = f"Connecting from LinkedIn / Growth framework at {job['company_name']}"
                    
                    execute_smtp_delivery(email, subject_line, email_body)
                    
                    cursor.execute("""
                        UPDATE outbound_pipeline SET status = 'EMAIL_SENT', resolved_email = ?, processed_at = ? WHERE id = ?
                    """, (email, datetime.now(), job['id']))
                except Exception as e:
                    cursor.execute("UPDATE outbound_pipeline SET status = 'DELIVERY_FAILED', processed_at = ? WHERE id = ?", (datetime.now(), job['id']))
            else:
                cursor.execute("UPDATE outbound_pipeline SET status = 'EMAIL_NOT_FOUND', processed_at = ? WHERE id = ?", (datetime.now(), job['id']))
        conn.commit()
