import pyotp

print("🔥 utils.totp cargado desde:", __file__)

def generate_totp_secret() -> str:
    return pyotp.random_base32()

def get_totp_uri(secret: str, email: str, issuer: str = "EunaStudio") -> str:
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)

def verify_totp(secret: str, code: str) -> bool:
    if not secret or not code:
        return False

    code = code.strip()

    if not code.isdigit() or len(code) != 6:
        return False

    totp = pyotp.TOTP(secret)

    # ⏱️ tolerancia segura para producción
    return totp.verify(code, valid_window=2)