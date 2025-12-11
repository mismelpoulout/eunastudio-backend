import json
import os
from datetime import datetime, timedelta

# Carpeta persistente en Render
DATA_FOLDER = "/data"
DB_PATH = os.path.join(DATA_FOLDER, "database.json")


def ensure_data_folder():
    """Crea /data si no existe (Render permite escribir aquí)."""
    os.makedirs(DATA_FOLDER, exist_ok=True)


def init_db():
    """Crea database.json si no existe."""
    ensure_data_folder()

    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump({"users": []}, f, indent=4)
        print("📁 Base de datos creada correctamente en:", DB_PATH)


def load_db():
    """Carga DB, corrige errores corruptos y ejecuta expiración automática."""
    init_db()

    try:
        with open(DB_PATH, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        # Si la DB está corrupta → reiniciamos
        data = {"users": []}
        save_db(data)

    # Ejecutar expiración automática del trial
    check_user_expiration(data)

    return data


def save_db(data):
    """Guarda DB en disco."""
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)


# -------------------------------------------------------
# 🔥 EXPIRACIÓN AUTOMÁTICA DEL TRIAL
# -------------------------------------------------------
def check_user_expiration(data):
    """
    Reglas oficiales:

    ✔ Usuario NO verificado → NO se bloquea
    ✔ Usuario con plan activo → NO se bloquea nunca
    ✔ Usuario verificado y sin plan → trial de 72 horas
         → si pasan 72h → BLOQUEADO automáticamente

    El bloqueo ocurre solo si `created_at` existe.
    """
    now = datetime.utcnow()
    modified = False

    for user in data.get("users", []):
        created_at = user.get("created_at")
        plan_active = user.get("plan_active", False)

        # 1️⃣ No verificado (created_at = None) → no se bloquea
        if not created_at:
            continue

        # 2️⃣ Plan activo → nunca se bloquea
        if plan_active:
            continue

        # Convertir fecha
        try:
            created_at_dt = datetime.fromisoformat(created_at)
        except Exception:
            continue  # evitar crash por formato inesperado

        # 3️⃣ Trial expirado
        if now - created_at_dt >= timedelta(hours=72):
            if not user.get("blocked", False):
                user["blocked"] = True
                user["blocked_at"] = now.isoformat()
                modified = True

    if modified:
        save_db(data)