import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import pytz

# Resolve paths
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
templates_dir = os.path.join(root_dir, "templates")

admin_template_path = os.path.join(templates_dir, "adminEmail.html")
user_template_path = os.path.join(templates_dir, "userConfirmation.html")

admin_template = ""
user_template = ""

try:
    with open(admin_template_path, "r", encoding="utf-8") as f:
        admin_template = f.read()
    with open(user_template_path, "r", encoding="utf-8") as f:
        user_template = f.read()
except Exception as e:
    print(f"[WARNING]  Could not load email templates: {e}")


def fill_template(template, data):
    # Replaces {{key}} with data[key]
    return re.sub(r"\{\{(\w+)\}\}", lambda match: str(data.get(match.group(1), "")), template)


def send_mail(to_email, subject, html_content, text_fallback):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 465))
    smtp_user = os.getenv("SMTP_USER") or os.getenv("GMAIL_USER")
    smtp_password = os.getenv("SMTP_PASSWORD") or os.getenv("GMAIL_APP_PASSWORD")

    if not smtp_user or not smtp_password:
        raise ValueError("SMTP credentials (SMTP_USER/SMTP_PASSWORD) not set in environment.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f'"Vizolane Technologies" <{smtp_user}>'
    msg["To"] = to_email

    msg.attach(MIMEText(text_fallback, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())


def send_admin_notification(data):
    tz = pytz.timezone("Asia/Kolkata")
    timestamp = datetime.now(tz).strftime("%d/%m/%Y, %I:%M:%S %p")

    name = data.get("name", "")
    email = data.get("email", "")
    phone = data.get("phone", "") or "Not provided"
    message = data.get("message", "")

    html_content = fill_template(admin_template, {
        "name": name,
        "email": email,
        "phone": phone,
        "message": message,
        "timestamp": timestamp
    })

    text_fallback = (
        f"New contact form submission:\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Phone: {phone}\n"
        f"Message: {message}\n"
        f"Time: {timestamp}"
    )

    admin_email = os.getenv("ADMIN_EMAIL")
    if not admin_email:
        raise ValueError("ADMIN_EMAIL not set in environment.")

    send_mail(admin_email, f"[CONTACT] New Contact: {name}", html_content, text_fallback)
    print("[SUCCESS] Admin notification sent")


def send_user_confirmation(data):
    name = data.get("name", "")
    email = data.get("email", "")
    message = data.get("message", "")

    html_content = fill_template(user_template, {
        "name": name,
        "message": message
    })

    text_fallback = (
        f"Hi {name},\n\n"
        f"Thank you for reaching out to Vizolane Technologies!\n\n"
        f"We've received your message:\n\"{message}\"\n\n"
        f"Our team will get back to you within 24 hours.\n\n"
        f"Best regards,\n"
        f"Vizolane Technologies LLP"
    )

    send_mail(email, "Thanks for contacting Vizolane Technologies!", html_content, text_fallback)
    print(f"[SUCCESS] User confirmation sent to: {email}")


def verify_connection():
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 465))
    smtp_user = os.getenv("SMTP_USER") or os.getenv("GMAIL_USER")
    smtp_password = os.getenv("SMTP_PASSWORD") or os.getenv("GMAIL_APP_PASSWORD")

    if not smtp_user or not smtp_password:
        print("[ERROR] Email credentials missing.")
        return False
    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_password)
        print(f"[SUCCESS] Email service ready ({smtp_host})")
        return True
    except Exception as e:
        print(f"[ERROR] Email service error: {e}")
        return False
