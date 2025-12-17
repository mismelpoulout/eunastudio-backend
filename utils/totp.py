# utils/totp.py
import pyotp
import base64
import os


def generate_totp_secret() -> str:
    """
    Genera un secreto TOTP base32 compatible con Google Authenticator
    """
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str, issuer: str = "EunaStudio") -> str:
    """
    Genera la URI para QR (otpauth://)
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def verify_totp(secret: str, code: str) -> bool:
    """
    Verifica un código TOTP ingresado por el usuario
    """
    if not secret or not code:
        return False

    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)