from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta

from utils.db import get_connection
from utils.totp import verify_totp
from utils.limiter import limiter

auth = Blueprint("auth", __name__)

@auth.post("/login")
@limiter.limit("5 per minute")
def login():
    data = request.json or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    code = (data.get("code") or "").strip()

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT
            id,
            email,
            password_hash,
            totp_enabled,
            totp_secret,
            is_blocked,
            role
        FROM users
        WHERE email = %s
        LIMIT 1
    """, (email,))
    user = cur.fetchone()

    # ❌ Usuario o password incorrectos
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"msg": "Credenciales inválidas"}), 401

    # 🚫 Usuario bloqueado
    if user["is_blocked"]:
        return jsonify({"msg": "Usuario bloqueado"}), 403

    # 🔐 Verificar 2FA si está activado
    if user["totp_enabled"]:
        if not code or not verify_totp(user["totp_secret"], code):
            return jsonify({
                "msg": "Código 2FA inválido",
                "requires_2fa": True
            }), 401

    # 🎟️ Crear JWT persistente
    access_token = create_access_token(
        identity={
            "user_id": user["id"],
            "role": user["role"]
        },
        expires_delta=timedelta(days=7)  # ✅ sesión persistente
    )

    return jsonify({
        "msg": "Login OK",
        "token": access_token,
        "email": user["email"],
        "role": user["role"]
    }), 200