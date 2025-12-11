import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave_secreta_dev")
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://usuario:password@localhost/mi_base"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SENDER = os.getenv("MAIL_SENDER", "tu_correo@gmail.com")
    MAIL_SENDER_PASSWORD = os.getenv("MAIL_PASSWORD", "password-correo")