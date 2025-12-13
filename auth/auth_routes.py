from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from utils.json_db import load_db, save_db
from utils.save_trial import save_trial_end
from utils.email_sender import send_verification_email
from utils.password_reset_email import send_password_reset_email
from datetime import datetime, timedelta
import jwt
import os

auth = Blueprint("auth", __name__)

# ------------------------------------------------------------
# CONFIG JWT
# ------------------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "CAMBIA_ESTA_CLAVE_SECRETA")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = 24


# ------------------------------------------------------------
# ✔ Función auxiliar: buscar usuario por email normalizado
# ------------------------------------------------------------
def find_user(email, db):
    email = email.strip().lower()
    for u in db.get("users", []):
        if u["email"].lower() == email:
            return u
    return None


# ------------------------------------------------------------
#               VERIFICAR EMAIL (Activar Trial)
# ------------------------------------------------------------
@auth.post("/verify")
def verify():
    data = request.json
    email = data.get("email", "").strip().lower()
    code = data.get("code")

    db = load_db()
    user = find_user(email, db)

    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    if user.get("is_verified"):
        return jsonify({"msg": "La cuenta ya está verificada"}), 400

    if user.get("verification_code") != code:
        return jsonify({"msg": "Código incorrecto"}), 400

    now = datetime.utcnow()
    trial_end = now + timedelta(hours=72)

    user["is_verified"] = True
    user["verification_code"] = None
    user["blocked"] = False
    user["blocked_at"] = None
    user["created_at"] = now.isoformat()
    user["trial_end"] = trial_end.isoformat()

    save_db(db)
    save_trial_end(user["id"], trial_end.isoformat())

    return jsonify({
        "msg": "Cuenta verificada correctamente",
        "trial_start": now.isoformat(),
        "trial_end": trial_end.isoformat()
    }), 200


# ------------------------------------------------------------
#                     LOGIN + JWT
# ------------------------------------------------------------
@auth.post("/login")
def login():
    data = request.json
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"msg": "Email y contraseña obligatorios"}), 400

    db = load_db()
    user = find_user(email, db)

    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    if not check_password_hash(user["password"], password):
        return jsonify({"msg": "Credenciales incorrectas"}), 400

    if not user.get("is_verified"):
        return jsonify({
            "msg": "Tu cuenta no está verificada",
            "action": "verify_required"
        }), 401

    if user.get("blocked", False):
        return jsonify({
            "msg": "Tu cuenta está bloqueada",
            "blocked": True,
            "blocked_at": user.get("blocked_at"),
            "plan_active": user.get("plan_active", False)
        }), 403

    payload = {
        "sub": user["id"],
        "email": user["email"],
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return jsonify({
        "msg": "Login exitoso",
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "plan_active": user.get("plan_active", False),
            "blocked": user.get("blocked", False),
            "created_at": user.get("created_at"),
            "trial_end": user.get("trial_end")
        }
    }), 200


# ------------------------------------------------------------
#             RECUPERAR CONTRASEÑA (ENVÍA EMAIL)
# ------------------------------------------------------------
@auth.post("/forgot-password")
def forgot_password():
    data = request.json
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"msg": "Correo requerido"}), 400

    db = load_db()
    user = find_user(email, db)

    # 🔐 No revelar si existe o no
    if not user:
        return jsonify({
            "msg": "Si el correo existe, enviaremos instrucciones.",
            "action": "email_not_found"
        }), 200

    payload = {
        "sub": user["id"],
        "email": user["email"],
        "type": "password_reset",
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    sent = send_password_reset_email(user["email"], token)

    if not sent:
        return jsonify({"msg": "No se pudo enviar el correo"}), 500

    return jsonify({
        "msg": "Te enviamos un correo para restablecer tu contraseña."
    }), 200


# ------------------------------------------------------------
#            RESET CONTRASEÑA (CON TOKEN)
# ------------------------------------------------------------
@auth.post("/reset-password")
def reset_password():
    data = request.json
    token = data.get("token")
    new_password = data.get("password")

    if not token or not new_password:
        return jsonify({"msg": "Datos incompletos"}), 400

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "password_reset":
            raise Exception("Token inválido")
    except jwt.ExpiredSignatureError:
        return jsonify({"msg": "El enlace expiró"}), 401
    except Exception:
        return jsonify({"msg": "Token inválido"}), 401

    db = load_db()
    user_id = payload["sub"]

    for u in db.get("users", []):
        if u["id"] == user_id:
            u["password"] = generate_password_hash(new_password)
            save_db(db)
            return jsonify({"msg": "Contraseña actualizada correctamente"}), 200

    return jsonify({"msg": "Usuario no encontrado"}), 404


# ------------------------------------------------------------
#                ACTIVAR PLAN (Suscripción)
# ------------------------------------------------------------
@auth.post("/plan/activate")
def activate_plan():
    data = request.json
    email = data.get("email", "").strip().lower()

    db = load_db()
    user = find_user(email, db)

    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    user["plan_active"] = True
    user["blocked"] = False
    user["blocked_at"] = None

    save_db(db)

    return jsonify({"msg": "Plan activado correctamente"}), 200


# ------------------------------------------------------------
#                 ESTADO COMPLETO DEL USUARIO
# ------------------------------------------------------------
@auth.get("/user/status")
def user_status():
    email = request.args.get("email", "").strip().lower()

    db = load_db()
    user = find_user(email, db)

    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    return jsonify({
        "email": user["email"],
        "plan_active": user.get("plan_active", False),
        "blocked": user.get("blocked", False),
        "created_at": user.get("created_at"),
        "blocked_at": user.get("blocked_at"),
        "trial_end": user.get("trial_end"),
        "is_verified": user.get("is_verified", False)
    }), 200