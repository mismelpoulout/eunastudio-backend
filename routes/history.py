# routes/history.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.history_service import (
    create_history_entry,
    get_user_history,
)

history = Blueprint("history", __name__, url_prefix="/history")


# ==================================================
# ➕ GUARDAR ESTADÍSTICA
# ==================================================
@history.post("/")
@jwt_required()
def save_history():
    identity = get_jwt_identity()
    user_id = identity.get("user_id")

    if not user_id:
        return jsonify({"msg": "Token inválido"}), 401

    data = request.json or {}

    required_fields = [
        "type",
        "correct",
        "incorrect",
        "total",
        "percentage",
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"Falta campo requerido: {field}"}), 400

    create_history_entry(
        user_id=user_id,
        type=data["type"],
        specialty=data.get("specialty"),
        correct=data["correct"],
        incorrect=data["incorrect"],
        total=data["total"],
        percentage=data["percentage"],
    )

    return jsonify({"msg": "Historial guardado"}), 201


# ==================================================
# 📥 OBTENER HISTORIAL DEL USUARIO
# ==================================================
@history.get("/")
@jwt_required()
def fetch_history():
    identity = get_jwt_identity()
    user_id = identity.get("user_id")

    if not user_id:
        return jsonify({"msg": "Token inválido"}), 401

    history = get_user_history(user_id)
    return jsonify(history), 200