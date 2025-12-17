import logging
from flask import Flask
from flask_cors import CORS

from auth.auth_routes import auth
from auth.totp_routes import totp_bp
from registro.registro_routes import registro

logging.basicConfig(level=logging.INFO)

def create_app():
    app = Flask(__name__)

    # 🔥 CORS GLOBAL
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        max_age=3600,
    )

    # 🔥 CORS EXPLÍCITO EN BLUEPRINTS (CLAVE)
    CORS(auth)
    CORS(totp_bp)
    CORS(registro)

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(totp_bp, url_prefix="/auth")
    app.register_blueprint(registro, url_prefix="/registro")

    @app.route("/", methods=["GET"])
    def home():
        return {"msg": "EunaStudio Backend OK"}

    return app


app = create_app()