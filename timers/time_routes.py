from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from timers.time_service import (
    get_global_usage_time,
    get_plan_remaining_time,
)

time_bp = Blueprint("time", __name__)

# ==================================================
# ⏱️ Relojes del usuario
# ==================================================
@time_bp.get("/time/status")
@jwt_required()
def time_status():
    """
    Devuelve:
    - Tiempo total usado en evaluaciones
    - Tiempo restante del plan
    """
    identity = get_jwt_identity()

    user_id = identity.get("user_id")
    if not user_id:
        return jsonify({"msg": "Token inválido"}), 401

    global_usage = get_global_usage_time(user_id)
    plan_remaining = get_plan_remaining_time(user_id)

    return jsonify({
        "usage": global_usage,
        "plan_remaining": plan_remaining
    }), 200