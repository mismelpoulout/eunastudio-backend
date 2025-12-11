import smtplib
from email.message import EmailMessage
import os

MAIL_SENDER = os.getenv("MAIL_SENDER")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")


def send_verification_email(to_email: str, code: str) -> bool:
    if not MAIL_SENDER or not MAIL_PASSWORD:
        print("⚠️ MAIL_SENDER o MAIL_PASSWORD no configurados")
        return False

    msg = EmailMessage()
    msg["Subject"] = "Verifica tu cuenta en Eunastudio"
    msg["From"] = MAIL_SENDER
    msg["To"] = to_email

    msg.set_content(
        f"""
Hola,

Gracias por registrarte en Eunastudio.

Tu código de verificación es: {code}

Cópialo y pégalo en la pantalla de verificación de la app/web.

Si no fuiste tú quien registró esta cuenta, puedes ignorar este mensaje.

Saludos,
Eunastudio
"""
    )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(MAIL_SENDER, MAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("ERROR ENVIANDO EMAIL:", e)
        return False