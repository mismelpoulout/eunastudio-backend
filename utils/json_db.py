import json
import os
from datetime import datetime, timedelta

# -------------------------------------------------------
# 📁 RUTA LOCAL COMPATIBLE CON RENDER FREE
# -------------------------------------------------------

# Carpeta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Carpeta local para datos (NO /data)
DATA_FOLDER = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_FOLDER, "database.json")


def ensure_data_folder():
    """Crea la carpeta data/ si no existe."""
    os.makedirs(DATA_FOLDER, exist_ok=True)


def init_db():
    """Crea database.json si no existe."""
    ensure_data_folder()

    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump({"users": []}, f, indent=4, ensure_ascii=False)

        print("📁 Base de datos creada correctamente en:", DB_PATH)


def load_db():
    """Carga DB, corrige errores y ejecuta expiración automática."""
    init_db()

    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        # DB corrupta → reiniciar
        data = {"users": []}
        save_db(data)

    # Ejecutar expiración automática del trial
    check_user_expiration(data)

    return data


def save_db(data):
    """Guarda DB en disco."""
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# -------------------------------------------------------
# 🔥 EXPIRACIÓN AUTOMÁTICA DEL TRIAL
# -------------------------------------------------------
def check_user_expiration(data):
    """
    Reglas:

    ✔ Usuario NO verificado → NO se bloquea
    ✔ Usuario con plan activo → NO se bloquea
    ✔ Usuario verificado y sin plan → trial de 72 horas
       → si pasan 72h → BLOQUEADO
    """
    now = datetime.utcnow()
    modified = False

    for user in data.get("users", []):
        created_at = user.get("created_at")
        plan_active = user.get("plan_active", False)

        # No verificado → no bloquear
        if not created_at:
            continue

        # Plan activo → nunca bloquear
        if plan_active:
            continue

        try:
            created_at_dt = datetime.fromisoformat(created_at)
        except Exception:
            continue

        if now - created_at_dt >= timedelta(hours=72):
            if not user.get("blocked", False):
                user["blocked"] = True
                user["blocked_at"] = now.isoformat()
                modified = True

    if modified:
        save_db(data)