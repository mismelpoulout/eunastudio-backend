# ==================================================
# 🔍 STATUS DEL USUARIO (FRONTEND)
# ==================================================
@auth.get("/user/status")
@jwt_required()
def user_status():
    identity = get_jwt_identity()

    if not identity or "user_id" not in identity:
        return jsonify({"msg": "Token inválido"}), 401

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT
            id,
            email,
            username,
            avatar,
            role,
            plan,
            is_blocked,
            totp_enabled
        FROM users
        WHERE id = %s
        LIMIT 1
    """, (identity["user_id"],))

    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    return jsonify({
        "authenticated": True,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["username"],
            "avatar": user["avatar"],
            "role": user["role"],
            "plan": user["plan"],
            "blocked": bool(user["is_blocked"]),
            "twofa_enabled": bool(user["totp_enabled"]),
        }
    }), 200