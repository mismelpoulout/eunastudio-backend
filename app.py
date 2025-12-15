import os
from flask import Flask
from flask_cors import CORS

from auth.auth_routes import auth
from registro.registro_routes import registro


def create_app():
    app = Flask(__name__)

    CORS(app, resources={r"/*": {"origins": "*"}})

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(registro, url_prefix="/registro")

    @app.get("/")
    def home():
        return {"msg": "Servidor funcionando ✔"}

    return app


app = create_app()