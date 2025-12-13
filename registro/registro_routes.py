from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from utils.json_db import load_db, save_db
from utils.validator import is_valid_password
from utils.email_sender import send_verification_email
import uuid
import random

registro = Blueprint("registro", __name__)


# ------------------------------------------------------------
#               REGISTRO DE USUARIO
# ------------------------------------------------------------
@registro.post("/signup")
def signup_user():
    data = request.json or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()

    # ---------------- VALIDACIONES ----------------
    if not email or not password:
        return jsonify({"msg": "Email y contraseña son obligatorios"}), 400

    if not is_valid_password(password):
        return jsonify({
            "msg": "La contraseña no cumple con los requisitos de seguridad.",
            "action": "invalid_password"
        }), 400

    db = load_db()

    # ---------------- USUARIO EXISTENTE ----------------
    for u in db.get("users", []):
        if u["email"].lower() == email:

            if not u.get("is_verified"):
                return jsonify({
                    "msg": "Este correo ya está registrado pero no verificado.",
                    "action": "verify_pending"
                }), 400

            return jsonify({
                "msg": "Este correo ya está registrado.",
                "action": "email_exists"
            }), 400

    # ---------------- CREAR USUARIO ----------------
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

    # ---------------- ENVIAR EMAIL ----------------
    email_sent = send_verification_email(email, verification_code)

    if not email_sent:
        return jsonify({
            "msg": "El usuario fue creado, pero no pudimos enviar el correo de verificación.",
            "action": "email_failed"
        }), 500

    # ---------------- RESPUESTA OK ----------------
    return jsonify({
        "msg": "Usuario registrado correctamente. Revisa tu correo para validar tu cuenta."
    }), 201