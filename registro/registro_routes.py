from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from utils.validator import is_valid_password
from utils.email_sender import send_verification_email
from utils.db import get_connection
import uuid
import random

registro = Blueprint("registro", __name__)

# ------------------------------------------------------------
#               REGISTRO DE USUARIO (MySQL)
# ------------------------------------------------------------
@registro.post("/signup")
def signup_user():
    data = request.json or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()

    print("📩 Registrando usuario:", email)

    # ---------------- VALIDACIONES ----------------
    if not email or not password or not name:
        return jsonify({"msg": "Nombre, email y contraseña son obligatorios"}), 400

    if not is_valid_password(password):
        return jsonify({
            "msg": "La contraseña no cumple con los requisitos de seguridad.",
            "action": "invalid_password"
        }), 400

    conn = None
    try:
        conn = get_connection()

        with conn.cursor() as cur:
            # ---------------- USUARIO EXISTENTE ----------------
            cur.execute("SELECT id, is_verified FROM users WHERE email=%s", (email,))
            existing = cur.fetchone()

            if existing:
                if not existing["is_verified"]:
                    return jsonify({
                        "msg": "Este correo ya está registrado pero no verificado.",
                        "action": "verify_pending"
                    }), 400

                return jsonify({
                    "msg": "Este correo ya está registrado.",
                    "action": "email_exists"
                }), 400

            # ---------------- CREAR USUARIO ----------------
            user_id = str(uuid.uuid4())
            verification_code = str(random.randint(100000, 999999))

            print("🔑 Código de verificación generado:", verification_code)

            cur.execute("""
                INSERT INTO users (
                    id,
                    email,
                    name,
                    password_hash,
                    verification_code,
                    is_verified,
                    role
                ) VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                user_id,
                email,
                name,
                generate_password_hash(password),
                verification_code,
                False,
                "user"
            ))

        # ---------------- ENVIAR EMAIL ----------------
        email_sent = send_verification_email(email, verification_code)

        if not email_sent:
            print("⚠️ Usuario creado pero falló envío de email")
            return jsonify({
                "msg": "La cuenta fue creada, pero no pudimos enviar el correo de verificación.",
                "action": "email_failed"
            }), 500

        print("✅ Usuario creado y correo enviado correctamente")

        return jsonify({
            "msg": "Usuario registrado correctamente. Revisa tu correo para validar tu cuenta."
        }), 201

    except Exception as e:
        print("❌ ERROR REGISTRO:", e)
        return jsonify({
            "msg": "Error interno al crear la cuenta"
        }), 500

    finally:
        if conn:
            conn.close()