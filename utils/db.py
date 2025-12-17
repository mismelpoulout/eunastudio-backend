# utils/db.py
import os
import mysql.connector
from mysql.connector import Error


def get_connection():
    host = os.getenv("MYSQLHOST")
    port = int(os.getenv("MYSQLPORT", 3306))
    user = os.getenv("MYSQLUSER")
    password = os.getenv("MYSQLPASSWORD")
    database = os.getenv("MYSQLDATABASE")

    # Validación temprana (muy importante en Railway)
    if not all([host, user, password, database]):
        raise RuntimeError(
            "❌ Faltan variables MySQL: "
            "MYSQLHOST, MYSQLUSER, MYSQLPASSWORD, MYSQLDATABASE"
        )

    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            autocommit=True,
            connection_timeout=10
        )

        if not conn.is_connected():
            raise RuntimeError("❌ Conexión MySQL creada pero no activa")

        return conn

    except Error as e:
        print("❌ ERROR MySQL:", str(e))
        raise