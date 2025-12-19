from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_connection
from utils.limiter import limiter
import uuid

comments = Blueprint("comments", __name__)

@comments.post("/")
@jwt_required()
@limiter.limit("5 per minute")  # rate-limit SOLO comentarios
def create_comment():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"msg": "Comentario vacío"}), 400

    # Normalmente identity = email (string)
    identity = get_jwt_identity()
    email = (identity or "").strip().lower()

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # Buscar user real
        cur.execute("""
            SELECT id, username, profile_image
            FROM users
            WHERE email = %s
            LIMIT 1
        """, (email,))
        user = cur.fetchone()

        if not user:
            return jsonify({"msg": "Usuario no encontrado"}), 404

        comment_id = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO comments (id, user_id, user_name, avatar, text)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            comment_id,
            user["id"],
            user["username"],
            user.get("profile_image"),
            text
        ))

        # autocommit=True en tu get_connection(), pero igual ok:
        conn.commit()

        # devuelve el comentario creado para que el front lo pinte altiro
        return jsonify({
            "id": comment_id,
            "user_name": user["username"],
            "avatar": user.get("profile_image"),
            "text": text
        }), 201

    except Exception as e:
        print("❌ ERROR create_comment:", e)
        if conn:
            conn.rollback()
        return jsonify({"msg": "Error interno"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@comments.get("/")
def list_comments():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 5))
    offset = (page - 1) * limit

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT id, user_name, avatar, text, created_at
            FROM comments
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))

        rows = cur.fetchall()
        return jsonify(rows), 200

    except Exception as e:
        print("❌ ERROR list_comments:", e)
        return jsonify({"msg": "Error interno"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()