import smtplib
from email.message import EmailMessage
import os

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_verification_email(to_email: str, code: str) -> bool:
    if not SMTP_USER or not SMTP_PASSWORD:
        print("⚠️ Variables SMTP no configuradas")
        return False

    msg = EmailMessage()
    msg["Subject"] = "Verifica tu cuenta en Eunastudio"
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    msg.set_content(f"""
Hola,

Tu código de verificación es: {code}

Eunastudio
""")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(msg)

        print("✅ Email enviado")
        return True

    except Exception as e:
        print("❌ ERROR SMTP:", e)
        return False