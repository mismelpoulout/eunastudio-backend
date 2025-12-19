# services/history_service.py
from utils.db import get_connection


# ==================================================
# ➕ INSERTAR REGISTRO
# ==================================================
def create_history_entry(
    user_id: str,
    type: str,
    correct: int,
    incorrect: int,
    total: int,
    percentage: float,
    specialty: str | None = None,
):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        """
        INSERT INTO history (
            user_id,
            type,
            specialty,
            correct,
            incorrect,
            total,
            percentage
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user_id,
            type,
            specialty,
            correct,
            incorrect,
            total,
            percentage,
        ),
    )

    conn.commit()
    cur.close()
    conn.close()


# ==================================================
# 📥 OBTENER HISTORIAL POR USUARIO
# ==================================================
def get_user_history(user_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        """
        SELECT
            id,
            type,
            specialty,
            correct,
            incorrect,
            total,
            percentage,
            created_at
        FROM history
        WHERE user_id = %s
        ORDER BY created_at ASC
        """,
        (user_id,),
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": r["id"],
            "type": r["type"],
            "specialty": r["specialty"],
            "correct": r["correct"],
            "incorrect": r["incorrect"],
            "total": r["total"],
            "percentage": float(r["percentage"]),
            "created_at": r["created_at"].isoformat(),
        }
        for r in rows
    ]