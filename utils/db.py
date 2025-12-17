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

    if not all([host, user, password, database]):
        raise RuntimeError(
            "❌ Faltan variables MySQL (MYSQLHOST, MYSQLUSER, MYSQLPASSWORD, MYSQLDATABASE)"
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
            raise RuntimeError("❌ No se pudo conectar a MySQL")

        return conn

    except Error as e:
        print("❌ ERROR MySQL:", e)
        raise