from flask import Blueprint, jsonify
from utils.db import get_connection

debug_db = Blueprint("debug_db", __name__)

@debug_db.get("/debug/db")
def test_db():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT 1 as ok")
        row = cur.fetchone()
    conn.close()
    return jsonify(row), 200