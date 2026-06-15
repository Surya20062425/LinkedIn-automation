import asyncio
import sqlite3
from datetime import datetime
from database import DB_NAME
from email_engine import resolve_corporate_email, build_professional_template, execute_smtp_delivery

async def process_outbound_queue():
    """Polls database asynchronously for accepted connections that passed the time lock."""
    while True:
        current_time = datetime.now()
        
        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Select leads where current time is greater than their scheduled delay time
            cursor.execute("""
                SELECT * FROM outbound_pipeline 
                WHERE status = 'CONNECTION_ACCEPTED' AND datetime(scheduled_email_at) <= datetime(?)
            """, (current_time,))
            active_jobs = cursor.fetchall()
            
            for job in active_jobs:
                print(f"[QUEUE] Dispatched job found for: {job['first_name']} {job['last_name']}")
                
                # 1. Email Resolution Block
                email = resolve_corporate_email(job['first_name'], job['last_name'], job['company_domain'])
                
                if email:
                    try:
                        # 2. Build personalized email copy
                        email_body = build_professional_template(job['first_name'], job['company_name'], job['industry_vertical'])
                        subject_line = f"Connecting from LinkedIn / Growth framework at {job['company_name']}"
                        
                        # 3. Deliver email
                        execute_smtp_delivery(email, subject_line, email_body)
                        
                        cursor.execute("""
                            UPDATE outbound_pipeline SET status = 'EMAIL_SENT', resolved_email = ?, processed_at = ? WHERE id = ?
                        """, (email, datetime.now(), job['id']))
                    except Exception as e:
                        print(f"[DELIVERY ERROR] SMTP Failure on Job {job['id']}: {e}")
                        cursor.execute("UPDATE outbound_pipeline SET status = 'DELIVERY_FAILED', processed_at = ? WHERE id = ?", (datetime.now(), job['id']))
                else:
                    cursor.execute("UPDATE outbound_pipeline SET status = 'EMAIL_NOT_FOUND', processed_at = ? WHERE id = ?", (datetime.now(), job['id']))
            conn.commit()
            
        await asyncio.sleep(30)  # Polling execution checks loop every 30 seconds
