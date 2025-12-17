import logging
from flask import Flask
from flask_cors import CORS

from auth.auth_routes import auth
from auth.totp_routes import totp_bp
from registro.registro_routes import registro

# Logs claros pero sin ruido excesivo
logging.basicConfig(level=logging.INFO)

def create_app():
    app = Flask(__name__)

    # 🔥 CORS GLOBAL (permite frontend local y Railway)
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=False
    )

    # Blueprints
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(totp_bp, url_prefix="/auth")
    app.register_blueprint(registro, url_prefix="/registro")

    @app.route("/", methods=["GET"])
    def home():
        return {"msg": "EunaStudio Backend OK"}

    return app


# 🎯 Gunicorn entrypoint
app = create_app()