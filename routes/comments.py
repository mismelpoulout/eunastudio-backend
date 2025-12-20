import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_connection
from utils.limiter import limiter

comments = Blueprint("comments", __name__)

# --------------------------------------------------
# ➕ Crear comentario (rate-limit SOLO aquí)
# --------------------------------------------------
@comments.post("")
@jwt_required()
@limiter.limit("5 per minute")
def create_comment():
    data = request.get_json(silent=True)

    # -----------------------------
    # Validación robusta
    # -----------------------------
    if not data or "text" not in data:
        return jsonify({"msg": "text must be a string"}), 400

    text = data.get("text")

    if not isinstance(text, str) or not text.strip():
        return jsonify({"msg": "text must be a string"}), 400

    text = text.strip()

    # -----------------------------
    # Identidad JWT
    # -----------------------------
    identity = get_jwt_identity()

    # 👉 Si el JWT guarda solo email
    if isinstance(identity, str):
        user_email = identity

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT id, username, avatar FROM users WHERE email = %s",
            (user_email,)
        )
        user = cur.fetchone()

        if not user:
            cur.close()
            conn.close()
            return jsonify({"msg": "Usuario no encontrado"}), 404

        user_id = user["id"]
        user_name = user["username"]
        avatar = user.get("avatar")

    # 👉 Si el JWT guarda un dict completo
    elif isinstance(identity, dict):
        user_id = identity.get("id")
        user_name = identity.get("name")
        avatar = identity.get("avatar")

    else:
        return jsonify({"msg": "Token inválido"}), 401

    # -----------------------------
    # Insert comentario
    # -----------------------------
    comment_id = str(uuid.uuid4())

    cur.execute(
        """
        INSERT INTO comments (id, user_id, user_name, avatar, text)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (comment_id, user_id, user_name, avatar, text),
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "id": comment_id,
        "user_name": user_name,
        "avatar": avatar,
        "text": text,
    }), 201


# --------------------------------------------------
# 📄 Listar comentarios (paginado)
# --------------------------------------------------
@comments.get("")
def list_comments():
    page = max(int(request.args.get("page", 1)), 1)
    limit = 5
    offset = (page - 1) * limit

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        """
        SELECT id, user_name, avatar, text, created_at
        FROM comments
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """,
        (limit, offset),
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows), 200