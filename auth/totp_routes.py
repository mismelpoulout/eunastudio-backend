from flask import Blueprint, request, jsonify
from utils.db import get_connection
from utils.totp import generate_totp_secret, get_totp_uri, verify_totp

totp_bp = Blueprint("totp", __name__)

@totp_bp.post("/2fa/setup")
def setup_2fa():
    data = request.json or {}
    email = data.get("email")

    secret = generate_totp_secret()
    uri = get_totp_uri(secret, email)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET totp_secret=%s WHERE email=%s",
        (secret, email)
    )

    return jsonify({"qr_uri": uri})


@totp_bp.post("/2fa/verify")
def verify_2fa():
    data = request.json or {}
    email = data.get("email")
    code = data.get("code")

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT totp_secret FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if not user or not verify_totp(user["totp_secret"], code):
        return jsonify({"msg": "Código inválido"}), 400

    cur.execute(
        "UPDATE users SET totp_enabled=1 WHERE email=%s",
        (email,)
    )

    return jsonify({"msg": "2FA activado"})