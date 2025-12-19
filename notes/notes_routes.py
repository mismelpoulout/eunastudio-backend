from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_connection

notes_bp = Blueprint("notes", __name__)

# ==================================================
# 📥 OBTENER NOTAS DEL USUARIO
# ==================================================
@notes_bp.get("/")
@jwt_required()
def get_notes():
    user_id = get_jwt_identity()["user_id"]

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT id, title, content, section, specialty, created_at
        FROM user_notes
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))

    notes = cur.fetchall()
    return jsonify(notes), 200


# ==================================================
# ➕ CREAR NOTA
# ==================================================
@notes_bp.post("/")
@jwt_required()
def create_note():
    user_id = get_jwt_identity()["user_id"]
    data = request.json or {}

    title = data.get("title")
    content = data.get("content")
    section = data.get("section")
    specialty = data.get("specialty")

    if not title or not content:
        return jsonify({"msg": "Título y contenido son obligatorios"}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO user_notes (user_id, title, content, section, specialty)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, title, content, section, specialty))

    conn.commit()

    return jsonify({"msg": "Nota creada"}), 201


# ==================================================
# ✏️ EDITAR NOTA
# ==================================================
@notes_bp.put("/<int:note_id>")
@jwt_required()
def update_note(note_id):
    user_id = get_jwt_identity()["user_id"]
    data = request.json or {}

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE user_notes
        SET title = %s, content = %s, section = %s, specialty = %s
        WHERE id = %s AND user_id = %s
    """, (
        data.get("title"),
        data.get("content"),
        data.get("section"),
        data.get("specialty"),
        note_id,
        user_id
    ))

    conn.commit()

    return jsonify({"msg": "Nota actualizada"}), 200


# ==================================================
# 🗑 ELIMINAR NOTA
# ==================================================
@notes_bp.delete("/<int:note_id>")
@jwt_required()
def delete_note(note_id):
    user_id = get_jwt_identity()["user_id"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM user_notes
        WHERE id = %s AND user_id = %s
    """, (note_id, user_id))

    conn.commit()

    return jsonify({"msg": "Nota eliminada"}), 200