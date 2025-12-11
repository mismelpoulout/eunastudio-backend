from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from utils.json_db import load_db, save_db
from utils.validator import is_valid_password
import uuid
import random

registro = Blueprint("registro", __name__)


@registro.post("/signup")
def signup_user():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    # Validación básica
    if not email or not password:
        return jsonify({"msg": "Email y contraseña son obligatorios"}), 400

    # Validación de contraseña segura
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

    # -----------------------------------------
    # 🚫 EVITAR REGISTRO DUPLICADO
    # -----------------------------------------
    for u in db["users"]:
        if u["email"] == email:

            if not u["is_verified"]:
                return jsonify({
                    "msg": "Este email ya está registrado, pero aún no fue verificado.",
                    "action": "verify_pending"
                }), 400

            return jsonify({
                "msg": "El email ya está registrado.",
                "action": "email_exists"
            }), 400

    # -----------------------------------------
    # REGISTRO NUEVO
    # -----------------------------------------

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
        "created_at": None,
        "trial_end": None,
        "blocked_at": None
    }

    db["users"].append(new_user)
    save_db(db)

    return jsonify({
        "msg": "Usuario registrado correctamente. Revisa tu correo para validar la cuenta.",
        "verification_code": verification_code
    }), 201
