import json
import os
from datetime import datetime, timedelta

DB_PATH = "database.json"


def load_db():
    """
    Carga la base de datos desde el archivo JSON.
    Si no existe, lo crea con estructura inicial.
    Además ejecuta el control automático de expiración.
    """
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump({"users": []}, f, indent=4)

    with open(DB_PATH, "r") as f:
        data = json.load(f)

    # Ejecutar control de expiración en cada carga
    check_user_expiration(data)

    return data


def save_db(data):
    """Guarda la base de datos JSON."""
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)


def check_user_expiration(data):
    """
    Bloquea automáticamente a todos los usuarios que:
    - NO tengan plan activo
    - Hayan verificado su cuenta (porque si no, created_at es None)
    - Hayan excedido las 72 horas desde created_at
    """
    now = datetime.utcnow()

    for user in data["users"]:
        created_at_str = user.get("created_at")
        plan_active = user.get("plan_active", False)

        # Si NO ha verificado email → created_at es None → NO se bloquea nunca
        if not created_at_str:
            continue

        # Convertir created_at a datetime
        try:
            created_at = datetime.fromisoformat(created_at_str)
        except Exception:
            continue  # evita errores si el formato está dañado

        # Si tiene plan activo → nunca se bloquea
        if plan_active:
            continue

        # Si pasaron más de 72h desde el inicio del trial
        if now - created_at >= timedelta(hours=72):
            if not user.get("blocked", False):
                user["blocked"] = True
                user["blocked_at"] = now.isoformat()

    # Guardar cambios después de actualizar estados
    save_db(data)