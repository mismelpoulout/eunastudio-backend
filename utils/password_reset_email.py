import smtplib
from email.message import EmailMessage
import os

MAIL_SENDER = os.getenv("MAIL_SENDER")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def send_password_reset_email(to_email: str, token: str) -> bool:
    if not MAIL_SENDER or not MAIL_PASSWORD:
        print("⚠️ MAIL_SENDER o MAIL_PASSWORD no configurados")
        return False

    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    msg = EmailMessage()
    msg["Subject"] = "Restablecer contraseña - Eunastudio"
    msg["From"] = MAIL_SENDER
    msg["To"] = to_email

    msg.set_content(f"""
Hola,

Recibimos una solicitud para restablecer tu contraseña en Eunastudio.

Haz clic en el siguiente enlace (válido por 15 minutos):

{reset_link}

Si no solicitaste este cambio, puedes ignorar este correo.

Saludos,
Eunastudio
""")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(MAIL_SENDER, MAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("❌ Error enviando email de recuperación:", e)
        return False