from flask import Blueprint, request, jsonify
from utils.db import get_connection
from utils.totp import verify_totp

totp_bp = Blueprint("totp", __name__)

@totp_bp.post("/2fa/verify")
def verify_2fa():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    code = (data.get("code") or "").strip()

    if not email or not code or not code.isdigit() or len(code) != 6:
        return jsonify({"msg": "Código inválido"}), 400

    conn = cur = None

    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT totp_secret, totp_enabled FROM users WHERE email = %s",
            (email,)
        )
        user = cur.fetchone()

        if not user or not user["totp_secret"]:
            return jsonify({"msg": "Código inválido"}), 400

        if not verify_totp(user["totp_secret"], code):
            return jsonify({"msg": "Código inválido"}), 400

        if not user["totp_enabled"]:
            cur.execute(
                "UPDATE users SET totp_enabled = 1 WHERE email = %s",
                (email,)
            )
            conn.commit()

        return jsonify({"twofa_enabled": True}), 200

    except Exception as e:
        print("❌ ERROR 2FA VERIFY:", e)
        return jsonify({"msg": "Error interno"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()