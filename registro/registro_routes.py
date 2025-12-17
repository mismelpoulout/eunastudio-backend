from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from utils.db import get_connection
from utils.totp import generate_totp_secret, get_totp_uri
import uuid
import qrcode
import io
import base64

registro = Blueprint("registro", __name__)

@registro.post("/signup")
def signup():
    data = request.json or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()

    if not email or not password or not name:
        return jsonify({"msg": "Datos incompletos"}), 400

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # 🔍 Verificar si ya existe
    cur.execute("SELECT id FROM users WHERE email=%s", (email,))
    if cur.fetchone():
        return jsonify({"msg": "Email ya registrado"}), 400

    # 🔐 Generar TOTP
    totp_secret = generate_totp_secret()
    otpauth_uri = get_totp_uri(totp_secret, email)

    user_id = str(uuid.uuid4())

    # 💾 Guardar usuario (2FA aún desactivado)
    cur.execute("""
        INSERT INTO users (
            id,
            email,
            name,
            password_hash,
            totp_secret,
            totp_enabled,
            created_at
        )
        VALUES (%s,%s,%s,%s,%s,0,NOW())
    """, (
        user_id,
        email,
        name,
        generate_password_hash(password),
        totp_secret
    ))

    conn.commit()

    # 🧾 Generar QR en base64
    qr = qrcode.make(otpauth_uri)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return jsonify({
        "msg": "Usuario creado. Escanea el QR para activar 2FA.",
        "user_id": user_id,
        "qr_base64": qr_base64,
        "otpauth_uri": otpauth_uri,
        "twofa_enabled": False
    }), 201