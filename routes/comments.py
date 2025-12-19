from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_connection
from utils.limiter import limiter
import uuid

comments = Blueprint("comments", __name__)

# 🔐 Rate limit SOLO comentarios
@comments.post("/")
@jwt_required()
@limiter.limit("5 per minute")   # 👈 CLAVE
def create_comment():
    data = request.json or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"msg": "Comentario vacío"}), 400

    user = get_jwt_identity()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO comments (id, user_id, user_name, avatar, text)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        str(uuid.uuid4()),
        user["id"],
        user["username"],
        user.get("profile_image"),
        text
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"msg": "Comentario guardado"}), 201


# 📥 Listar comentarios (PAGINADO)
@comments.get("/")
def list_comments():
    page = int(request.args.get("page", 1))
    limit = 5
    offset = (page - 1) * limit

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT user_name, avatar, text, created_at
        FROM comments
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (limit, offset))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows)