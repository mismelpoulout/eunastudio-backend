from datetime import datetime, timedelta
from utils.db import get_connection


# ==================================================
# ⏱️ TIEMPO TOTAL USADO EN EVALUACIONES
# ==================================================
def get_global_usage_time(user_id: str) -> dict:
    """
    Suma el tiempo usado en:
    - simulaciones
    - exámenes
    - trivia
    - especialidades
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT COALESCE(SUM(duration_seconds), 0) AS total_seconds
        FROM history
        WHERE user_id = %s
    """, (user_id,))

    row = cur.fetchone()
    total_seconds = int(row["total_seconds"] or 0)

    cur.close()
    conn.close()

    return _seconds_to_hms(total_seconds)


# ==================================================
# ⏳ TIEMPO RESTANTE DEL PLAN
# ==================================================
def get_plan_remaining_time(user_id: str) -> dict:
    """
    Calcula el tiempo restante del plan (trial o pago)
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT plan, plan_expires_at
        FROM users
        WHERE id = %s
        LIMIT 1
    """, (user_id,))

    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user or not user["plan_expires_at"]:
        return {
            "expired": True,
            "remaining": _seconds_to_hms(0)
        }

    now = datetime.utcnow()
    expires_at = user["plan_expires_at"]

    remaining_seconds = max(
        int((expires_at - now).total_seconds()),
        0
    )

    return {
        "expired": remaining_seconds == 0,
        "remaining": _seconds_to_hms(remaining_seconds)
    }


# ==================================================
# 🔧 UTILIDAD
# ==================================================
def _seconds_to_hms(seconds: int) -> dict:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return {
        "hours": hours,
        "minutes": minutes,
        "seconds": secs,
        "total_seconds": seconds
    }