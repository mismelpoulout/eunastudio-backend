import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_connection
from utils.limiter import limiter

comments = Blueprint("comments", __name__)

# ==================================================
# ➕ Crear comentario (JWT + rate limit)
# ==================================================
@comments.post("")
@jwt_required()
@limiter.limit("5 per minute")
def create_comment():
    data = request.get_json(silent=True) or {}

    text = data.get("text")

    # -----------------------------
    # Validación estricta
    # -----------------------------
    if not isinstance(text, str) or not text.strip():
        return jsonify({"msg": "text must be a string"}), 400

    text = text.strip()

    # -----------------------------
    # JWT Identity (FIJO)
    # -----------------------------
    identity = get_jwt_identity()

    if not identity or "user_id" not in identity:
        return jsonify({"msg": "Token inválido"}), 401

    user_id = identity["user_id"]

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # -----------------------------
    # Obtener datos del usuario
    # -----------------------------
    cur.execute(
        """
        SELECT username, avatar
        FROM users
        WHERE id = %s
        LIMIT 1
        """,
        (user_id,)
    )

    user = cur.fetchone()

    if not user:
        cur.close()
        conn.close()
        return jsonify({"msg": "Usuario no encontrado"}), 404

    comment_id = str(uuid.uuid4())

    # -----------------------------
    # Insert comentario
    # -----------------------------
    cur.execute(
        """
        INSERT INTO comments (id, user_id, user_name, avatar, text)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            comment_id,
            user_id,
            user["username"],
            user.get("avatar"),
            text,
        )
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "id": comment_id,
        "user_name": user["username"],
        "avatar": user.get("avatar"),
        "text": text,
    }), 201


# ==================================================
# 📄 Listar comentarios (paginado)
# ==================================================
@comments.get("")
def list_comments():
    page = max(int(request.args.get("page", 1)), 1)
    limit = 6
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
        (limit, offset)
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows), 200