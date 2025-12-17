from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from utils.db import get_connection
from utils.totp import verify_totp
from utils.limiter import limiter   # ✅ IMPORTAR limiter GLOBAL

import uuid
import hashlib
from datetime import datetime, timedelta

password_bp = Blueprint("password", __name__)

# ─────────────────────────────────────────────
# 1️⃣ VERIFICAR IDENTIDAD CON GOOGLE AUTHENTICATOR
# ─────────────────────────────────────────────
@password_bp.post("/recover/verify")
@limiter.limit("5 per minute")   # ✅ ahora sí existe
def verify_recovery():
    data = request.json or {}

    email = (data.get("email") or "").strip().lower()
    code = (data.get("code") or "").strip()

    if not email or not code:
        return jsonify({"msg": "Datos incompletos"}), 400

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT id, totp_secret, totp_enabled
        FROM users
        WHERE email = %s
        LIMIT 1
    """, (email,))
    user = cur.fetchone()

    # ⛔ Anti-enumeración
    if not user:
        return jsonify({
            "msg": "Si la cuenta existe y tiene 2FA, podrás continuar."
        }), 200

    if not user["totp_enabled"] or not user["totp_secret"]:
        return jsonify({
            "msg": "Esta cuenta no tiene 2FA activado. Recuperación no permitida.",
            "action": "2fa_not_enabled"
        }), 403

    if not verify_totp(user["totp_secret"], code):
        return jsonify({
            "msg": "Código de Google Authenticator inválido.",
            "action": "invalid_totp"
        }), 401

    # 🔐 Crear token seguro
    raw_token = str(uuid.uuid4())
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    cur.execute("""
        INSERT INTO password_resets (id, user_id, token_hash, expires_at)
        VALUES (%s, %s, %s, %s)
    """, (
        str(uuid.uuid4()),
        user["id"],
        token_hash,
        expires_at
    ))

    return jsonify({
        "msg": "Identidad verificada. Puedes cambiar tu contraseña.",
        "reset_token": raw_token,
        "expires_in": 300
    }), 200