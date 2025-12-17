from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from utils.validator import is_valid_password
from utils.db import get_connection
import uuid

registro = Blueprint("registro", __name__)

@registro.post("/signup")
def signup():
    data = request.json or {}

    email = data.get("email", "").lower()
    password = data.get("password", "")
    name = data.get("name", "")

    if not email or not password or not name:
        return jsonify({"msg": "Datos incompletos"}), 400

    if not is_valid_password(password):
        return jsonify({"msg": "Contraseña inválida"}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email=%s", (email,))
    if cur.fetchone():
        return jsonify({"msg": "Usuario ya existe"}), 400

    cur.execute("""
        INSERT INTO users (id, email, name, password_hash)
        VALUES (%s,%s,%s,%s)
    """, (
        str(uuid.uuid4()),
        email,
        name,
        generate_password_hash(password)
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"msg": "Usuario creado"}), 201