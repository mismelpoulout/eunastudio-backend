# utils/admin_required.py
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import jsonify

def admin_required(fn):
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()

        if identity.get("role") != "admin":
            return jsonify({"msg": "Acceso solo para administradores"}), 403

        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper