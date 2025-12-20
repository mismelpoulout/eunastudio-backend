from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from datetime import timedelta, datetime

from utils.db import get_connection
from utils.totp import verify_totp
from utils.limiter import limiter

# ==================================================
# 🔐 BLUEPRINT AUTH
# ==================================================
auth = Blueprint("auth", __name__)

TRIAL_HOURS = 72


# ==================================================
# 🔐 LOGIN
# ==================================================
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
            role,
            plan,
            plan_expires_at,
            created_at,
            totp_enabled,
            totp_secret,
            is_blocked
        FROM users
        WHERE email = %s
        LIMIT 1
    """, (email,))

    user = cur.fetchone()

    # ❌ Credenciales inválidas
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"msg": "Credenciales inválidas"}), 401

    is_admin = user["role"] == "admin"
    now = datetime.utcnow()
    blocked = False

    # ⏳ TRIAL (solo no admin)
    if not is_admin and user["plan"] == "trial":
        trial_end = user["created_at"] + timedelta(hours=TRIAL_HOURS)
        if now > trial_end:
            blocked = True

    # 💳 PLAN PAGADO (solo no admin)
    if not is_admin and user["plan"] in ("monthly", "quarterly"):
        if not user["plan_expires_at"] or now > user["plan_expires_at"]:
            blocked = True

    # 🚫 BLOQUEO
    if blocked:
        if not user["is_blocked"]:
            cur.execute(
                "UPDATE users SET is_blocked = 1 WHERE id = %s",
                (user["id"],)
            )
            conn.commit()

        return jsonify({
            "msg": "Plan vencido o período de prueba finalizado",
            "blocked": True
        }), 403

    # 🔐 2FA
    if user["totp_enabled"]:
        if not code or not verify_totp(user["totp_secret"], code):
            return jsonify({
                "msg": "Código 2FA inválido",
                "requires_2fa": True
            }), 401

    return _login_success(user)


# ==================================================
# 🔍 STATUS USUARIO (FRONTEND)
# ==================================================
@auth.get("/user/status")
@jwt_required()
def user_status():
    identity = get_jwt_identity()

    if not identity or "user_id" not in identity:
        return jsonify({"msg": "Token inválido"}), 401

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT role, plan, is_blocked
        FROM users
        WHERE id = %s
        LIMIT 1
    """, (identity["user_id"],))

    user = cur.fetchone()

    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    return jsonify({
        "role": user["role"],
        "plan": user["plan"],
        "blocked": bool(user["is_blocked"])
    }), 200


# ==================================================
# 🔑 LOGIN EXITOSO
# ==================================================
def _login_success(user):
    access_token = create_access_token(
        identity={
            "user_id": user["id"],
            "role": user["role"]
        },
        expires_delta=timedelta(days=7)
    )

    return jsonify({
        "msg": "Login OK",
        "token": access_token,
        "email": user["email"],
        "role": user["role"],
        "plan": user["plan"],
        "blocked": False
    }), 200