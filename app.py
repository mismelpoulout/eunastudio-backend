import logging
from flask import Flask
from flask_cors import CORS

from auth.auth_routes import auth
from registro.registro_routes import registro
from routes.test_email import test_email  # ✅ correcto

logging.basicConfig(level=logging.DEBUG)

def create_app():
    app = Flask(__name__)

    app.config["DEBUG"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = True

    CORS(app, resources={r"/*": {"origins": "*"}})

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(registro, url_prefix="/registro")
    app.register_blueprint(test_email)  # /test-email

    @app.get("/")
    def home():
        return {"msg": "Servidor funcionando ✔"}

    return app

app = create_app()