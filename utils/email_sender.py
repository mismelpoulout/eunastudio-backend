import smtplib
from email.message import EmailMessage
import os

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

SMTP_FROM = SMTP_USER  # 🔥 obligatorio con Gmail

def send_verification_email(to_email: str, code: str) -> bool:
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD]):
        print("⚠️ Variables SMTP no configuradas correctamente")
        return False

    msg = EmailMessage()
    msg["Subject"] = "Verifica tu cuenta en Eunastudio"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email

    msg.set_content(f"""
Hola,

Gracias por registrarte en Eunastudio.

Tu código de verificación es: {code}

Saludos,
Eunastudio
""")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(msg)

        print(f"✅ Email enviado a {to_email}")
        return True

    except Exception as e:
        print("❌ ERROR ENVIANDO EMAIL:", e)
        return False