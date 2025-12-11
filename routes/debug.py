from flask import Blueprint, jsonify
from utils.json_db import load_db

debug = Blueprint("debug", __name__)

@debug.get("/debug/users")
def get_users():
    db = load_db()
    return jsonify(db)
