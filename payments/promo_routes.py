from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_connection
from datetime import datetime

promo_bp = Blueprint("promo", __name__)

@promo_bp.post("/validate-promo")
@jwt_required()
def validate_promo():
    user_id = get_jwt_identity()
    data = request.json or {}
    code = (data.get("code") or "").strip().upper()

    if not code:
        return jsonify({"valido": False, "msg": "Código vacío"}), 400

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT id, descuento, expira_at, usado
        FROM promo_codes
        WHERE code=%s
        LIMIT 1
    """, (code,))
    promo = cur.fetchone()

    if not promo:
        return jsonify({"valido": False}), 200

    if promo["usado"]:
        return jsonify({"valido": False}), 200

    if promo["expira_at"] and datetime.utcnow() > promo["expira_at"]:
        return jsonify({"valido": False}), 200

    return jsonify({
        "valido": True,
        "descuento": promo["descuento"],
        "expira": int(promo["expira_at"].timestamp() * 1000)
        if promo["expira_at"] else None
    }), 200