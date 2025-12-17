import pyotp

def generate_totp_secret():
    return pyotp.random_base32()

def get_totp_uri(secret: str, email: str, issuer="EunaStudio"):
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)

def verify_totp_code(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code)