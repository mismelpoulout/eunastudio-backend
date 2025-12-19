from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from utils.db import get_connection
from utils.totp import generate_totp_secret, get_totp_uri
from utils.limiter import limiter

import uuid
import qrcode
import io
import base64
import logging

logger = logging.getLogger(__name__)

registro = Blueprint("registro", __name__)

@registro.post("/signup")
@limiter.limit("5 per minute")  # 🛡️ evita abuso
def signup():
    # --------------------------------------------------
    # 📥 INPUT
    # --------------------------------------------------
    if not request.is_json:
        return jsonify({"msg": "Formato JSON inválido"}), 400

    data = request.get_json(silent=True) or {}

    username = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not username or not email or not password:
        return jsonify({"msg": "Datos incompletos"}), 400

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # --------------------------------------------------
        # 🔍 EMAIL ÚNICO
        # --------------------------------------------------
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return jsonify({"msg": "Email ya registrado"}), 409

        # --------------------------------------------------
        # 🔐 PASSWORD
        # --------------------------------------------------
        password_hash = generate_password_hash(password)

        # --------------------------------------------------
        # 🔐 TOTP (NO ACTIVADO AÚN)
        # --------------------------------------------------
        totp_secret = generate_totp_secret()
        otpauth_uri = get_totp_uri(totp_secret, email)

        # --------------------------------------------------
        # ⏳ PLAN TRIAL (72H)
        # --------------------------------------------------
        trial_expires = datetime.utcnow() + timedelta(hours=72)

        user_id = str(uuid.uuid4())

        # --------------------------------------------------
        # 💾 INSERT
        # --------------------------------------------------
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
                %s, %s, %s, %s,
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

        logger.info(f"✅ Usuario creado: {email}")

    except Exception as e:
        if conn:
            conn.rollback()
        logger.exception("❌ ERROR SIGNUP")
        return jsonify({"msg": "Error interno al registrar usuario"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    # --------------------------------------------------
    # 🧾 QR BASE64
    # --------------------------------------------------
    qr = qrcode.make(otpauth_uri)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # --------------------------------------------------
    # 📤 RESPONSE
    # --------------------------------------------------
    return jsonify({
        "msg": "Usuario creado. Escanea el QR para activar 2FA.",
        "user_id": user_id,
        "qr_base64": qr_base64,
        "otpauth_uri": otpauth_uri,
        "twofa_enabled": False,
        "plan": "trial",
        "plan_expires_at": trial_expires.isoformat()
    }), 201