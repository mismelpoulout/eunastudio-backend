from datetime import datetime
from utils.db import get_connection
from timers.time_service import get_plan_remaining_time
from mailer import send_plan_warning_email

WARNING_HOURS = [24, 10, 1]  # avisos escalonados

def check_plans_and_notify():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT id, email
        FROM users
        WHERE plan_expires_at IS NOT NULL
    """)
    users = cur.fetchall()

    for user in users:
        result = get_plan_remaining_time(user["id"])
        remaining = result["remaining"]["total_seconds"]

        for hours in WARNING_HOURS:
            if remaining <= hours * 3600:
                send_plan_warning_email(
                    email=user["email"],
                    hours_left=hours
                )
                break

    cur.close()
    conn.close()