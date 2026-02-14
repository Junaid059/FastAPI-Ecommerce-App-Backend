from app.celery_app import celery_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# Email config (using smtplib for sync)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")

@celery_app.task
def send_email(subject: str, email_to: str, body: str):
    """
    Synchronous email sending using smtplib.
    """
    if not all([MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM]):
        raise ValueError("Missing email configuration in .env")
    if MAIL_USERNAME is None or MAIL_PASSWORD is None:
        raise ValueError("MAIL_USERNAME and MAIL_PASSWORD must not be None")
    if MAIL_FROM is None:
        raise ValueError("MAIL_FROM must not be None")
    
    msg = MIMEMultipart()
    msg['From'] = MAIL_FROM
    msg['To'] = email_to
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'html'))  
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_FROM, email_to, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Email send failed: {e}") 