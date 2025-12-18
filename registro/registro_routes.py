from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

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

    username = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not username or not email or not password:
        return jsonify({"msg": "Datos incompletos"}), 400

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # 🔍 Verificar si el email ya existe
    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cur.fetchone():
        return jsonify({"msg": "Email ya registrado"}), 409

    # 🔐 Password hash
    password_hash = generate_password_hash(password)

    # 🔐 Generar TOTP (pero NO activar todavía)
    totp_secret = generate_totp_secret()
    otpauth_uri = get_totp_uri(totp_secret, email)

    # ⏳ Trial 72 horas
    trial_expires = datetime.utcnow() + timedelta(hours=72)

    user_id = str(uuid.uuid4())

    # 💾 Insertar usuario
    cur.execute("""
        INSERT INTO users (
            id,
            username,
            email,
            password_hash,
            role,
            plan,
            plan_expires_at,
            totp_secret,
            totp_enabled,
            is_blocked,
            created_at
        ) VALUES (
            %s,
            %s,
            %s,
            %s,
            'user',
            'trial',
            %s,
            %s,
            0,
            0,
            NOW()
        )
    """, (
        user_id,
        username,
        email,
        password_hash,
        trial_expires,
        totp_secret
    ))

    conn.commit()

    # 🧾 Generar QR (base64)
    qr = qrcode.make(otpauth_uri)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return jsonify({
        "msg": "Usuario creado. Escanea el QR para activar 2FA.",
        "user_id": user_id,
        "qr_base64": qr_base64,
        "otpauth_uri": otpauth_uri,
        "twofa_enabled": False,
        "plan": "trial",
        "plan_expires_at": trial_expires.isoformat()
    }), 201