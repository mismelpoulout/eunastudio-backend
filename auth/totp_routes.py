from flask import Blueprint, request, jsonify
from utils.db import get_connection
from utils.totp import (
    generate_totp_secret,
    get_totp_uri,
    verify_totp_code
)
import qrcode
import io
import base64

totp_bp = Blueprint("totp", __name__)

# ------------------------------------------------------------
# 1️⃣ SETUP 2FA → GENERA QR PARA GOOGLE AUTHENTICATOR
# ------------------------------------------------------------
@totp_bp.post("/2fa/setup")
def setup_2fa():
    data = request.json or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"msg": "user_id requerido"}), 400

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # Obtener email del usuario
        cur.execute(
            "SELECT email FROM users WHERE id = %s",
            (user_id,)
        )
        user = cur.fetchone()

        if not user:
            return jsonify({"msg": "Usuario no encontrado"}), 404

        # Generar secreto TOTP
        secret = generate_totp_secret()

        # Guardar secreto (NO activar aún)
        cur.execute(
            "UPDATE users SET totp_secret = %s WHERE id = %s",
            (secret, user_id)
        )
        conn.commit()

        # Generar URI y QR
        uri = get_totp_uri(secret, user["email"])

        img = qrcode.make(uri)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        qr_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        return jsonify({
            "qr_base64": qr_base64,
            "manual_key": secret  # mostrar SOLO una vez
        }), 200

    except Exception as e:
        print("❌ ERROR 2FA SETUP:", e)
        return jsonify({"msg": "Error interno del servidor"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# ------------------------------------------------------------
# 2️⃣ VERIFY 2FA → CONFIRMA CÓDIGO Y ACTIVA TOTP
# ------------------------------------------------------------
@totp_bp.post("/2fa/verify")
def verify_2fa():
    data = request.json or {}
    user_id = data.get("user_id")
    code = data.get("code")

    if not user_id or not code:
        return jsonify({"msg": "user_id y code requeridos"}), 400

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT totp_secret FROM users WHERE id = %s",
            (user_id,)
        )
        user = cur.fetchone()

        if not user or not user["totp_secret"]:
            return jsonify({"msg": "2FA no configurado"}), 400

        if not verify_totp_code(user["totp_secret"], code):
            return jsonify({"msg": "Código inválido"}), 401

        # Activar TOTP
        cur.execute(
            "UPDATE users SET totp_enabled = 1 WHERE id = %s",
            (user_id,)
        )
        conn.commit()

        return jsonify({
            "msg": "2FA activado correctamente"
        }), 200

    except Exception as e:
        print("❌ ERROR 2FA VERIFY:", e)
        return jsonify({"msg": "Error interno del servidor"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()