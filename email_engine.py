import os
import smtplib
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "YOUR_API_KEY")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_SENDER = os.getenv("COMPANY_EMAIL", "exec@yourcompany.com")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "xxxx xxxx xxxx xxxx")

def resolve_corporate_email(first_name: str, last_name: str, domain: str) -> str:
    """Utilizes Hunter API to discover business emails with clean string handling."""
    url = f"https://api.hunter.io/v2/email-finder?domain={domain}&first_name={first_name}&last_name={last_name}&api_key={HUNTER_API_KEY}"
    try:
        with httpx.Client() as client:
            response = client.get(url, timeout=8.0)
            if response.status_code == 200:
                return response.json().get("data", {}).get("email")
    except Exception as e:
        print(f"[ERROR] Email Enrichment Call Failed: {e}")
    return None

def build_professional_template(first_name: str, company_name: str, vertical: str) -> str:
    """Generates structured, high-ticket executive b2b outreach copies."""
    fallback_industry = "your space" if not vertical or vertical == "General" else f"the {vertical} sector"
    
    body = (
        f"Hi {first_name},\n\n"
        f"Thanks for accepting my connection request on LinkedIn. I've been tracking structural changes "
        f"across {fallback_industry} for a bit, and found the work you are doing at {company_name} highly relevant.\n\n"
        f"We've been actively assisting scaling teams optimize their backend pipelines and thought it might be "
        f"worth opening a brief line of communication.\n\n"
        f"Are you open to a brief 10-minute introduction next Tuesday morning?\n\n"
        f"Best regards,\n\n"
        f"Managing Director\n"
        f"Enterprise Systems Corp."
    )
    return body

def execute_smtp_delivery(target_email: str, subject: str, message_body: str):
    """Fires a highly secure corporate email envelope via SSL."""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = target_email
    msg["Subject"] = subject
    
    msg.attach(MIMEText(message_body, "plain"))
    
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, [target_email], msg.as_string())
