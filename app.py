import os
import logging
from flask import Flask
from flask_cors import CORS

from auth.auth_routes import auth
from registro.registro_routes import registro

from routes.test_email import test_email

app.register_blueprint(test_email)

# 🔴 ACTIVAR LOGS DE ERROR REALES
logging.basicConfig(level=logging.DEBUG)

def create_app():
    app = Flask(__name__)

    # 🔴 FORZAR DEBUG Y PROPAGACIÓN DE ERRORES
    app.config["DEBUG"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = True

    # CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Blueprints
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(registro, url_prefix="/registro")

    @app.get("/")
    def home():
        return {"msg": "Servidor funcionando ✔"}

    return app


# 🔴 Gunicorn necesita esta variable expuesta
app = create_app()
