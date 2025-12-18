# admin/promo_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from datetime import datetime

from utils.db import get_connection
from utils.admin_required import admin_required
from utils.promo import generate_promo_code
import uuid

promo_bp = Blueprint("promo", __name__)

@promo_bp.post("/admin/promo-codes")
@admin_required
def create_promo_code():
    data = request.json or {}

    discount = data.get("discount")
    start_at = data.get("start_at")
    expires_at = data.get("expires_at")

    if not discount or not start_at or not expires_at:
        return jsonify({"msg": "Datos incompletos"}), 400

    code = generate_promo_code()
    promo_id = str(uuid.uuid4())
    admin = get_jwt_identity()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO promo_codes (
            id, code, discount, start_at, expires_at, created_by
        )
        VALUES (%s,%s,%s,FROM_UNIXTIME(%s/1000),FROM_UNIXTIME(%s/1000),%s)
    """, (
        promo_id,
        code,
        discount,
        start_at,
        expires_at,
        admin["user_id"]
    ))

    conn.commit()

    return jsonify({
        "msg": "Código promocional creado",
        "code": code,
        "discount": discount
    }), 201