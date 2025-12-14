# utils/db.py
import os
import pymysql
from pymysql.cursors import DictCursor

def get_connection():
    host = os.getenv("MYSQLHOST") or os.getenv("DB_HOST")
    port = int(os.getenv("MYSQLPORT") or os.getenv("DB_PORT") or 3306)
    user = os.getenv("MYSQLUSER") or os.getenv("DB_USER")
    password = os.getenv("MYSQLPASSWORD") or os.getenv("DB_PASSWORD")
    database = os.getenv("MYSQLDATABASE") or os.getenv("DB_NAME")

    if not all([host, user, password, database]):
        raise RuntimeError("Faltan variables MySQL (MYSQLHOST, MYSQLUSER, MYSQLPASSWORD, MYSQLDATABASE)")

    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        cursorclass=DictCursor,
        autocommit=True,
    )