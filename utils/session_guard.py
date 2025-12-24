from flask_jwt_extended import get_jwt_identity
from utils.db import get_connection


def check_active_session() -> bool:
    """
    Verifica que el JWT corresponda a la sesión activa del usuario.
    Retorna False si:
    - El token no tiene identidad válida
    - El usuario no existe
    - El session_id no coincide (login en otro dispositivo)
    """

    identity = get_jwt_identity()

    if not identity:
        return False

    user_id = identity.get("user_id")
    token_session_id = identity.get("session_id")

    if not user_id or not token_session_id:
        return False

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        """
        SELECT active_session_id
        FROM users
        WHERE id = %s
        LIMIT 1
        """,
        (user_id,),
    )

    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return False

    # 🔐 Sesión válida solo si coincide exactamente
    return user["active_session_id"] == token_session_id