from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from utils.db import get_connection
from utils.totp import verify_totp

auth = Blueprint("auth", __name__)


@auth.post("/login")
def login():
    data = request.json or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    code = data.get("code")  # TOTP opcional

    if not email or not password:
        return jsonify({"msg": "Email y contraseña requeridos"}), 400

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if not user or not check_password_hash(user["password_hash"], password):
            return jsonify({"msg": "Credenciales inválidas"}), 401

        # 🔐 2FA con Google Authenticator
        if user.get("totp_enabled"):
            if not user.get("totp_secret"):
                return jsonify({"msg": "2FA mal configurado"}), 500

            if not code or not verify_totp(user["totp_secret"], code):
                return jsonify({"msg": "Código 2FA inválido"}), 401

        return jsonify({
            "msg": "Login OK",
            "user_id": user["id"],
            "email": user["email"]
        }), 200

    except Exception as e:
        print("❌ ERROR LOGIN:", e)
        return jsonify({"msg": "Error interno del servidor"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()