from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from utils.validator import is_valid_password
from utils.email_sender import send_verification_email
from utils.db import get_connection
import uuid
import random
import traceback

registro = Blueprint("registro", __name__)

@registro.post("/signup")
def signup_user():
    data = request.json or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()

    print("📩 Registrando usuario:", email)

    if not name or not email or not password:
        return jsonify({
            "msg": "Nombre, correo y contraseña son obligatorios"
        }), 400

    if not is_valid_password(password):
        return jsonify({
            "msg": "La contraseña no cumple con los requisitos de seguridad",
            "action": "invalid_password"
        }), 400

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # --------- USUARIO EXISTENTE ---------
        cur.execute(
            "SELECT id, is_verified FROM users WHERE email = %s",
            (email,)
        )
        existing_user = cur.fetchone()

        if existing_user:
            if not existing_user["is_verified"]:
                return jsonify({
                    "msg": "Este correo ya está registrado pero no verificado.",
                    "action": "verify_pending"
                }), 400

            return jsonify({
                "msg": "Este correo ya está registrado.",
                "action": "email_exists"
            }), 400

        # --------- CREAR USUARIO ---------
        user_id = str(uuid.uuid4())
        verification_code = str(random.randint(100000, 999999))
        password_hash = generate_password_hash(password)

        print("🔑 Código de verificación:", verification_code)

        cur.execute("""
            INSERT INTO users (
                id,
                email,
                name,
                password_hash,
                verification_code,
                is_verified,
                role,
                plan,
                plan_start,
                plan_end,
                created_at
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
        """, (
            user_id,
            email,
            name,
            password_hash,
            verification_code,
            False,
            "user",
            "trial",
            None,
            None
        ))

        # ✅ COMMIT OBLIGATORIO
        conn.commit()

        # --------- ENVIAR EMAIL ---------
        email_sent = send_verification_email(email, verification_code)

        if not email_sent:
            print("⚠️ Email de verificación no enviado")
            return jsonify({
                "msg": "Cuenta creada, pero no se pudo enviar el correo de verificación.",
                "action": "email_failed"
            }), 201  # 👈 sigue siendo éxito

        print("✅ Usuario creado correctamente")

        return jsonify({
            "msg": "Usuario registrado correctamente. Revisa tu correo para validar tu cuenta."
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()

        print("❌ ERROR REGISTRO")
        print(traceback.format_exc())

        return jsonify({
            "msg": "Error interno del servidor",
            "error": str(e)
        }), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()