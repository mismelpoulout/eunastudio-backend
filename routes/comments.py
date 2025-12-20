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
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"msg": "Comentario vacío"}), 400

    user = get_jwt_identity()  # debe traer id, name, avatar
    user_id = user["id"]
    user_name = user["name"]
    avatar = user.get("avatar")

    comment_id = str(uuid.uuid4())

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        INSERT INTO comments (id, user_id, user_name, avatar, text)
        VALUES (%s, %s, %s, %s, %s)
    """, (comment_id, user_id, user_name, avatar, text))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "id": comment_id,
        "user_name": user_name,
        "avatar": avatar,
        "text": text
    }), 201


# --------------------------------------------------
# 📄 Listar comentarios (paginado)
# --------------------------------------------------
@comments.get("")
def list_comments():
    page = int(request.args.get("page", 1))
    limit = 5
    offset = (page - 1) * limit

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT id, user_name, avatar, text, created_at
        FROM comments
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (limit, offset))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows), 200