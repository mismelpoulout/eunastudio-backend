from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from utils.db import get_connection
from utils.totp import verify_totp
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

auth = Blueprint("auth", __name__)

@auth.post("/login")
@limiter.limit("5 per minute")
def login():
    data = request.json or {}

    email = (data.get("email") or "").lower()
    password = data.get("password") or ""
    code = data.get("code")

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"msg": "Credenciales inválidas"}), 401

    if user["totp_enabled"]:
        if not code or not verify_totp(user["totp_secret"], code):
            return jsonify({"msg": "Código 2FA inválido"}), 401

    return jsonify({"msg": "Login OK"}), 200