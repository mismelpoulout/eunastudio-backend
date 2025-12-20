from datetime import datetime
from utils.db import get_connection


# ==================================================
# 🗄️ CREAR TABLA SI NO EXISTE
# ==================================================
def ensure_time_table_exists():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_time_metrics (
            user_id VARCHAR(36) NOT NULL PRIMARY KEY,
            total_usage_seconds INT NOT NULL DEFAULT 0,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,
            CONSTRAINT fk_user_time_user
                FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


# ==================================================
# 🧍 CREAR FILA DE USUARIO SI NO EXISTE
# ==================================================
def ensure_user_row(user_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT IGNORE INTO user_time_metrics (user_id)
        VALUES (%s)
    """, (user_id,))

    conn.commit()
    cur.close()
    conn.close()


# ==================================================
# ⏱️ TIEMPO TOTAL USADO
# ==================================================
def get_global_usage_time(user_id: str) -> dict:
    ensure_time_table_exists()
    ensure_user_row(user_id)

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT total_usage_seconds
        FROM user_time_metrics
        WHERE user_id = %s
    """, (user_id,))

    row = cur.fetchone()
    total_seconds = int(row["total_usage_seconds"] or 0)

    cur.close()
    conn.close()

    return _seconds_to_hms(total_seconds)


# ==================================================
# ➕ SUMAR TIEMPO (cuando termina un examen)
# ==================================================
def add_usage_time(user_id: str, seconds: int):
    ensure_time_table_exists()
    ensure_user_row(user_id)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE user_time_metrics
        SET total_usage_seconds = total_usage_seconds + %s
        WHERE user_id = %s
    """, (seconds, user_id))

    conn.commit()
    cur.close()
    conn.close()


# ==================================================
# ⏳ TIEMPO RESTANTE DEL PLAN
# ==================================================
def get_plan_remaining_time(user_id: str) -> dict:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT plan_expires_at
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
            "reason": "no_plan",
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
        "reason": "expired" if remaining_seconds == 0 else "active",
        "remaining": _seconds_to_hms(remaining_seconds),
        "plan_expires_at": expires_at.isoformat()
    }
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT plan_expires_at
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
    remaining_seconds = max(
        int((user["plan_expires_at"] - now).total_seconds()),
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