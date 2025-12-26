import pyotp
from datetime import datetime

print("🔥 utils.totp cargado desde:", __file__)

# ==================================================
# 🔐 GENERAR SECRET (UNA SOLA VEZ POR USUARIO)
# ==================================================
def generate_totp_secret() -> str:
    """
    Genera un secreto Base32 compatible con Google Authenticator
    """
    return pyotp.random_base32()


# ==================================================
# 🔗 GENERAR URI PARA QR
# ==================================================
def get_totp_uri(secret: str, email: str, issuer: str = "EunaStudio") -> str:
    """
    Genera la URI estándar para Google Authenticator
    - 6 dígitos
    - 30 segundos
    - SHA1 (default)
    """
    totp = pyotp.TOTP(
        secret,
        digits=6,
        interval=30
    )
    return totp.provisioning_uri(
        name=email,
        issuer_name=issuer
    )


# ==================================================
# ✅ VERIFICAR CÓDIGO TOTP
# ==================================================
def verify_totp(secret: str, code: str) -> bool:
    """
    Verifica código TOTP con tolerancia de desfase de reloj
    valid_window=2 → ±60 segundos (2 ventanas)
    """
    if not secret or not code:
        return False

    # Limpieza defensiva
    code = "".join(code.split())

    if not code.isdigit() or len(code) != 6:
        return False

    totp = pyotp.TOTP(
        secret,
        digits=6,
        interval=30
    )

    # 🧠 Tolerancia segura para producción
    return totp.verify(code, valid_window=2)