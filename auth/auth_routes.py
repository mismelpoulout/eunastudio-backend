from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from utils.json_db import load_db, save_db
from utils.save_trial import save_trial_end
from datetime import datetime, timedelta

auth = Blueprint("auth", __name__)


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

    # Ya verificado
    if user.get("is_verified"):
        return jsonify({"msg": "La cuenta ya está verificada"}), 400

    # Código incorrecto
    if user.get("verification_code") != code:
        return jsonify({"msg": "Código incorrecto"}), 400

    # Activar cuenta
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
#                     LOGIN (Backend Full Control)
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

    # Contraseña incorrecta
    if not check_password_hash(user["password"], password):
        return jsonify({"msg": "Credenciales incorrectas"}), 400

    # Usuario NO verificado
    if not user.get("is_verified"):
        return jsonify({
            "msg": "Tu cuenta no está verificada",
            "action": "verify_required"
        }), 401

    # Usuario bloqueado (trial expirado)
    if user.get("blocked", False):
        return jsonify({
            "msg": "Tu cuenta está bloqueada",
            "blocked": True,
            "blocked_at": user.get("blocked_at"),
            "plan_active": user.get("plan_active", False)
        }), 403

    # LOGIN OK
    return jsonify({
        "msg": "Login exitoso",
        "user_id": user["id"],
        "email": user["email"],
        "plan_active": user["plan_active"],
        "blocked": user["blocked"],
        "created_at": user["created_at"],
        "trial_end": user.get("trial_end")
    }), 200


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

    # Activar plan y quitar bloqueo
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
        "plan_active": user["plan_active"],
        "blocked": user["blocked"],
        "created_at": user["created_at"],
        "blocked_at": user["blocked_at"],
        "trial_end": user.get("trial_end"),
        "is_verified": user.get("is_verified", False)
    }), 200