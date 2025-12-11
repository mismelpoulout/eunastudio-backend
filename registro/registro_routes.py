from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from utils.json_db import load_db, save_db
from utils.validator import is_valid_password
import uuid
import random

registro = Blueprint("registro", __name__)


# ------------------------------------------------------------
#               REGISTRO DE USUARIO
# ------------------------------------------------------------
@registro.post("/signup")
def signup_user():
    data = request.json
    email = data.get("email", "").strip().lower()   # ← normalizamos email
    password = data.get("password", "")
    name = data.get("name", "").strip()

    # Validación básica
    if not email or not password:
        return jsonify({"msg": "Email y contraseña son obligatorios"}), 400

    # Validación contraseña segura
    if not is_valid_password(password):
        return jsonify({
            "msg": "La contraseña no cumple con los requisitos de seguridad.",
            "requirements": {
                "min_length": "Mínimo 8 caracteres",
                "uppercase": "Al menos una letra mayúscula",
                "lowercase": "Al menos una letra minúscula",
                "number": "Al menos un número",
                "special_char": "Al menos un carácter especial (!@#$%^&*)"
            }
        }), 400

    db = load_db()

    # ------------------------------------------------------------
    # ✔ Verificar si el usuario YA existe
    # ------------------------------------------------------------
    for u in db["users"]:
        if u["email"].strip().lower() == email:

            # Caso: registrado pero NO verificado
            if not u["is_verified"]:
                return jsonify({
                    "msg": "Este correo ya está registrado, pero aún no fue verificado.",
                    "action": "verify_pending"
                }), 400

            # Caso: completamente registrado
            return jsonify({
                "msg": "Este correo ya está registrado.",
                "action": "email_exists"
            }), 400

    # ------------------------------------------------------------
    # ✔ Crear usuario nuevo
    # ------------------------------------------------------------
    verification_code = str(random.randint(100000, 999999))

    new_user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": name,
        "password": generate_password_hash(password),
        "is_verified": False,
        "verification_code": verification_code,
        "plan_active": False,
        "blocked": False,
        "blocked_at": None,
        "created_at": None,
        "trial_end": None
    }

    db["users"].append(new_user)
    save_db(db)

    # ------------------------------------------------------------
    # ⚠ En producción aquí deberías llamar a tu función de email
    # send_email_verification(email, verification_code)
    # ------------------------------------------------------------

    return jsonify({
        "msg": "Usuario registrado correctamente. Revisa tu correo para validar la cuenta.",
        "verification_code": verification_code  # ← visible solo en desarrollo
    }), 201