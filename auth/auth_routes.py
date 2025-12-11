from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from utils.json_db import load_db, save_db
from utils.save_trial import save_trial_end
from datetime import datetime, timedelta

auth = Blueprint("auth", __name__)


# -------------------------
#       VERIFICAR EMAIL
# -------------------------
@auth.post("/verify")
def verify():
    data = request.json
    email = data.get("email")
    code = data.get("code")

    db = load_db()

    for user in db["users"]:
        if user["email"] == email:

            # Código incorrecto
            if user["verification_code"] != code:
                return jsonify({"msg": "Código incorrecto"}), 400

            # ACTIVAR CUENTA
            now = datetime.utcnow()
            trial_end = now + timedelta(hours=72)
            trial_end_str = trial_end.isoformat()

            user["is_verified"] = True
            user["verification_code"] = None
            user["blocked"] = False
            user["blocked_at"] = None
            user["created_at"] = now.isoformat()
            user["trial_end"] = trial_end_str  # guardar en base principal

            save_db(db)

            # GUARDAR EL TIEMPO FINAL EN UN JSON PERMANENTE
            save_trial_end(user["id"], trial_end_str)

            return jsonify({
                "msg": "Cuenta verificada correctamente.",
                "trial_start": now.isoformat(),
                "trial_end": trial_end_str
            })

    return jsonify({"msg": "Usuario no encontrado"}), 404



# -------------------------
#           LOGIN
# -------------------------
@auth.post("/login")
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "Email y contraseña son obligatorios"}), 400

    db = load_db()

    for user in db["users"]:
        if user["email"] == email:

            # Contraseña incorrecta
            if not check_password_hash(user["password"], password):
                return jsonify({"msg": "Contraseña incorrecta"}), 400

            # Usuario NO verificado
            if not user["is_verified"]:
                return jsonify({"msg": "Tu cuenta no está verificada"}), 401

            # Usuario bloqueado
            if user.get("blocked", False):
                return jsonify({
                    "msg": "Tu cuenta está bloqueada",
                    "blocked": True,
                    "blocked_at": user.get("blocked_at")
                }), 403

            # LOGIN OK — devolver trial_end para el cronómetro
            return jsonify({
                "msg": "Login exitoso",
                "user_id": user["id"],
                "email": user["email"],
                "plan_active": user["plan_active"],
                "blocked": user["blocked"],
                "created_at": user["created_at"],
                "trial_end": user.get("trial_end")  # ← importante para el countdown
            })

    return jsonify({"msg": "Usuario no encontrado"}), 404



# -------------------------
#     ACTIVAR PLAN
# -------------------------
@auth.post("/plan/activate")
def activate_plan():
    data = request.json
    email = data.get("email")

    db = load_db()

    for user in db["users"]:
        if user["email"] == email:
            user["plan_active"] = True
            user["blocked"] = False
            user["blocked_at"] = None
            save_db(db)
            return jsonify({"msg": "Plan activado correctamente"})

    return jsonify({"msg": "Usuario no encontrado"}), 404



# -------------------------
#      ESTADO DEL USUARIO
# -------------------------
@auth.get("/user/status")
def user_status():
    email = request.args.get("email")

    db = load_db()

    for user in db["users"]:
        if user["email"] == email:
            return jsonify({
                "email": user["email"],
                "plan_active": user["plan_active"],
                "blocked": user["blocked"],
                "created_at": user["created_at"],
                "blocked_at": user["blocked_at"],
                "trial_end": user.get("trial_end")  # ← también lo damos aquí
            })

    return jsonify({"msg": "Usuario no encontrado"}), 404