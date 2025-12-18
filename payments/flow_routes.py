from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_connection
from utils.flow import create_flow_payment

flow_bp = Blueprint("flow", __name__)

@flow_bp.post("/create-flow")
@jwt_required()
def create_flow():
    user_id = get_jwt_identity()
    data = request.json or {}

    monto = data.get("monto")
    concepto = data.get("concepto")
    codigo = data.get("codigo")

    if not monto or not concepto:
        return jsonify({"msg": "Datos incompletos"}), 400

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT email, username
        FROM users
        WHERE id=%s
    """, (user_id,))
    user = cur.fetchone()

    token = create_flow_payment(
        email=user["email"],
        name=user["username"],
        amount=monto,
        concept=concepto
    )

    if not token:
        return jsonify({"msg": "Error creando pago"}), 500

    return jsonify({"token": token}), 200