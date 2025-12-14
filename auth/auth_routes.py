from flask import Blueprint, request, jsonify, g
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta, timezone
import jwt
import os

from utils.db import get_connection
from utils.email_sender import send_verification_email
from utils.password_reset_email import send_password_reset_email

auth = Blueprint("auth", __name__)

# ------------------------------------------------------------
# CONFIG JWT
# ------------------------------------------------------------
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CAMBIA_ESTA_CLAVE")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# ------------------------------------------------------------
# Helpers JWT
# ------------------------------------------------------------
def create_token(user: dict) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user["id"],
        "email": user["email"],
        "role": user.get("role", "user"),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=JWT_EXP_HOURS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

def get_bearer_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.replace("Bearer ", "").strip()

def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = get_bearer_token()
        if not token:
            return jsonify({"msg": "Token faltante"}), 401
        try:
            payload = decode_token(token)
            g.user = payload
            return fn(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"msg": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"msg": "Token inválido"}), 401
    return wrapper

# ------------------------------------------------------------
# LOGIN (MySQL + JWT)
# ------------------------------------------------------------
@auth.post("/login")
def login():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"msg": "Email y contraseña obligatorios"}), 400

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, email, password_hash, name, is_verified, role,
                       plan_active, blocked, created_at, trial_end
                FROM users
                WHERE email = %s
                LIMIT 1
            """, (email,))
            user = cur.fetchone()

        if not user:
            return jsonify({"msg": "Usuario no encontrado"}), 404

        if not check_password_hash(user["password_hash"], password):
            return jsonify({"msg": "Credenciales incorrectas"}), 400

        if not user["is_verified"]:
            return jsonify({
                "msg": "Cuenta no verificada",
                "action": "verify_required"
            }), 401

        if user["blocked"]:
            return jsonify({
                "msg": "Cuenta bloqueada",
                "blocked": True,
                "plan_active": bool(user["plan_active"])
            }), 403

        token = create_token(user)

        return jsonify({
            "msg": "Login exitoso",
            "token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"],
                "plan_active": bool(user["plan_active"]),
                "blocked": bool(user["blocked"]),
                "created_at": user["created_at"],
                "trial_end": user["trial_end"]
            }
        }), 200

    except Exception as e:
        print("❌ ERROR LOGIN:", e)
        return jsonify({"msg": "Error interno en login"}), 500
    finally:
        if conn:
            conn.close()

# ------------------------------------------------------------
# VERIFICAR EMAIL
# ------------------------------------------------------------
@auth.post("/verify")
def verify_email():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    code = data.get("code")

    if not email or not code:
        return jsonify({"msg": "Datos incompletos"}), 400

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, verification_code, is_verified
                FROM users
                WHERE email=%s
            """, (email,))
            user = cur.fetchone()

            if not user:
                return jsonify({"msg": "Usuario no encontrado"}), 404

            if user["is_verified"]:
                return jsonify({"msg": "La cuenta ya está verificada"}), 400

            if user["verification_code"] != code:
                return jsonify({"msg": "Código incorrecto"}), 400

            now = datetime.utcnow()
            trial_end = now + timedelta(hours=72)

            cur.execute("""
                UPDATE users
                SET is_verified=1,
                    verification_code=NULL,
                    created_at=%s,
                    trial_end=%s,
                    blocked=0,
                    blocked_at=NULL
                WHERE id=%s
            """, (now, trial_end, user["id"]))

        return jsonify({
            "msg": "Cuenta verificada correctamente",
            "trial_end": trial_end
        }), 200

    except Exception as e:
        print("❌ ERROR VERIFY:", e)
        return jsonify({"msg": "Error interno"}), 500
    finally:
        if conn:
            conn.close()

# ------------------------------------------------------------
# RECUPERAR CONTRASEÑA (ENVÍA EMAIL)
# ------------------------------------------------------------
@auth.post("/forgot-password")
def forgot_password():
    data = request.json or {}
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"msg": "Correo requerido"}), 400

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, email FROM users WHERE email=%s", (email,))
            user = cur.fetchone()

        # 🔐 No revelar existencia
        if not user:
            return jsonify({
                "msg": "Si el correo existe, enviaremos instrucciones."
            }), 200

        payload = {
            "sub": user["id"],
            "type": "password_reset",
            "exp": int((datetime.utcnow() + timedelta(minutes=15)).timestamp())
        }

        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        send_password_reset_email(user["email"], token)

        return jsonify({
            "msg": "Te enviamos un correo para restablecer tu contraseña."
        }), 200

    except Exception as e:
        print("❌ ERROR FORGOT:", e)
        return jsonify({"msg": "Error interno"}), 500
    finally:
        if conn:
            conn.close()

# ------------------------------------------------------------
# RESET CONTRASEÑA
# ------------------------------------------------------------
@auth.post("/reset-password")
def reset_password():
    data = request.json or {}
    token = data.get("token")
    new_password = data.get("password")

    if not token or not new_password:
        return jsonify({"msg": "Datos incompletos"}), 400

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "password_reset":
            return jsonify({"msg": "Token inválido"}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({"msg": "El enlace expiró"}), 401
    except Exception:
        return jsonify({"msg": "Token inválido"}), 401

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users
                SET password_hash=%s
                WHERE id=%s
            """, (generate_password_hash(new_password), payload["sub"]))

        return jsonify({"msg": "Contraseña actualizada correctamente"}), 200

    except Exception as e:
        print("❌ ERROR RESET:", e)
        return jsonify({"msg": "Error interno"}), 500
    finally:
        if conn:
            conn.close()

# ------------------------------------------------------------
# STATUS USUARIO (JWT)
# ------------------------------------------------------------
@auth.get("/user/status")
@login_required
def user_status():
    user_id = g.user["sub"]

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT email, plan_active, blocked, created_at, trial_end, is_verified
                FROM users
                WHERE id=%s
            """, (user_id,))
            u = cur.fetchone()

        if not u:
            return jsonify({"msg": "Usuario no encontrado"}), 404

        return jsonify({
            "email": u["email"],
            "plan_active": bool(u["plan_active"]),
            "blocked": bool(u["blocked"]),
            "created_at": u["created_at"],
            "trial_end": u["trial_end"],
            "is_verified": bool(u["is_verified"])
        }), 200

    except Exception as e:
        print("❌ ERROR STATUS:", e)
        return jsonify({"msg": "Error interno"}), 500
    finally:
        if conn:
            conn.close()