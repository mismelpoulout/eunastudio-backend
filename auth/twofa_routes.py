from flask import Blueprint, request, jsonify
import pyotp
import qrcode
import base64
from io import BytesIO
from utils.db import get_connection

twofa = Blueprint("twofa", __name__)

@twofa.post("/setup")
def setup_2fa():
    user_id = request.json["user_id"]

    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=user_id, issuer_name="EunaStudio")

    img = qrcode.make(uri)
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET totp_secret=%s WHERE id=%s",
        (secret, user_id)
    )
    conn.commit()

    return jsonify({
        "qr": base64.b64encode(buffer.getvalue()).decode(),
        "secret": secret
    })

@twofa.post("/confirm")
def confirm_2fa():
    data = request.json
    user_id = data["user_id"]
    code = data["code"]

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT totp_secret FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()

    if not pyotp.TOTP(user["totp_secret"]).verify(code):
        return jsonify({"msg": "Código inválido"}), 400

    cur.execute(
        "UPDATE users SET totp_enabled=1 WHERE id=%s",
        (user_id,)
    )
    conn.commit()

    return jsonify({"msg": "2FA activado"})