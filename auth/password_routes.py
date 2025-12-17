from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from utils.db import get_connection
from utils.totp import verify_totp
import time
import uuid

password_bp = Blueprint("password", __name__)

# ─────────────────────────────────────────────
# 1️⃣ VERIFICAR IDENTIDAD CON GOOGLE AUTHENTICATOR
# ─────────────────────────────────────────────
@password_bp.post("/recover/verify")
def verify_recovery():
    data = request.json or {}

    email = data.get("email", "").lower()
    code = data.get("code", "")

    if not email or not code:
        return jsonify({"msg": "Datos incompletos"}), 400

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT id, totp_secret, totp_enabled
        FROM users
        WHERE email = %s
    """, (email,))
    user = cur.fetchone()

    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    if not user["totp_enabled"] or not user["totp_secret"]:
        return jsonify({
            "msg": "Esta cuenta no tiene 2FA activado. Recuperación no permitida."
        }), 403

    if not verify_totp(user["totp_secret"], code):
        return jsonify({"msg": "Código de Google Authenticator inválido"}), 401

    # Token temporal (solo en memoria / frontend)
    reset_token = str(uuid.uuid4())

    # ⏱️ Opcional: puedes guardar este token en DB con expiración
    # o simplemente usar user_id directamente (más simple)

    return jsonify({
        "msg": "Identidad verificada",
        "reset_allowed": True,
        "user_id": user["id"],
        "token": reset_token,
        "expires_in": 300  # 5 minutos
    }), 200


# ─────────────────────────────────────────────
# 2️⃣ RESETEAR CONTRASEÑA (POST-VERIFICACIÓN)
# ─────────────────────────────────────────────
@password_bp.post("/recover/reset")
def reset_password():
    data = request.json or {}

    user_id = data.get("user_id")
    new_password = data.get("new_password")

    if not user_id or not new_password:
        return jsonify({"msg": "Datos incompletos"}), 400

    if len(new_password) < 8:
        return jsonify({"msg": "La contraseña es muy corta"}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET password_hash = %s
        WHERE id = %s
    """, (
        generate_password_hash(new_password),
        user_id
    ))

    if cur.rowcount == 0:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    return jsonify({
        "msg": "Contraseña actualizada correctamente"
    }), 200