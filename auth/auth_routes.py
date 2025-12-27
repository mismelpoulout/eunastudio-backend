import uuid
from datetime import timedelta

from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

from utils.db import get_connection
from utils.totp import verify_totp
from utils.limiter import limiter

auth = Blueprint("auth", __name__)

TRIAL_HOURS = 72
TRIAL_SECONDS = TRIAL_HOURS * 3600


# ==================================================
# 🔐 LOGIN (NUNCA BLOQUEA)
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
            totp_enabled,
            totp_secret
        FROM users
        WHERE email = %s
        LIMIT 1
    """, (email,))
    user = cur.fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        cur.close()
        conn.close()
        return jsonify({"msg": "Credenciales inválidas"}), 401

    if user["totp_enabled"]:
        if not code or not verify_totp(user["totp_secret"], code):
            cur.close()
            conn.close()
            return jsonify({
                "msg": "Código 2FA inválido",
                "requires_2fa": True
            }), 401

    cur.close()
    conn.close()

    return _login_success(user)


# ==================================================
# 🔍 STATUS USUARIO (FUENTE DE LA VERDAD)
# ==================================================
@auth.get("/user/status")
@jwt_required()
def user_status():
    identity = get_jwt_identity()

    # ✅ identity YA ES el dict correcto
    if not isinstance(identity, dict):
        return jsonify({"msg": "Token inválido"}), 401

    user_id = identity.get("user_id")
    if not user_id:
        return jsonify({"msg": "Token inválido"}), 401

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT
            id,
            role,
            plan,
            is_blocked,

            CASE
              WHEN role <> 'admin'
                   AND plan = 'trial'
                   AND created_at IS NOT NULL
                   AND TIMESTAMPDIFF(SECOND, created_at, UTC_TIMESTAMP()) >= %s
              THEN 1

              WHEN role <> 'admin'
                   AND plan IN ('monthly','quarterly')
                   AND (plan_expires_at IS NULL OR plan_expires_at <= UTC_TIMESTAMP())
              THEN 1

              ELSE 0
            END AS blocked

        FROM users
        WHERE id = %s
        LIMIT 1
    """, (TRIAL_SECONDS, user_id))

    user = cur.fetchone()

    if not user:
        cur.close()
        conn.close()
        return jsonify({"msg": "Usuario no encontrado"}), 404

    blocked = bool(user["blocked"])

    # 🔒 Persistir bloqueo
    if blocked and not user["is_blocked"]:
        cur.execute(
            "UPDATE users SET is_blocked = 1 WHERE id = %s",
            (user_id,)
        )
        conn.commit()

    cur.close()
    conn.close()

    return jsonify({
        "role": user["role"],
        "plan": user["plan"],
        "blocked": blocked
    }), 200

# ==================================================
# 🔑 LOGIN EXITOSO (SESIÓN ÚNICA)
# ==================================================
def _login_success(user):
    session_id = str(uuid.uuid4())

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET active_session_id = %s
        WHERE id = %s
    """, (session_id, user["id"]))

    conn.commit()
    cur.close()
    conn.close()

    access_token = create_access_token(
        identity={
            "user_id": user["id"],
            "role": user["role"],
            "session_id": session_id
        },
        expires_delta=timedelta(days=7)
    )

    return jsonify({
        "msg": "Login OK",
        "token": access_token,
        "email": user["email"],
        "role": user["role"],
        "plan": user["plan"]
    }), 200