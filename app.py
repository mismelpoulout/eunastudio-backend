import logging
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

from utils.limiter import limiter
from auth.auth_routes import auth

logging.basicConfig(level=logging.INFO)

def create_app():
    app = Flask(__name__)

    # --------------------------------------------------
    # 🔐 JWT CONFIG
    # --------------------------------------------------
    app.config["JWT_SECRET_KEY"] = os.environ.get(
        "JWT_SECRET_KEY", "dev-secret-no-usar-en-prod"
    )
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

    jwt = JWTManager(app)

    # --------------------------------------------------
    # 🌍 CORS (DEV + PROD)
    # --------------------------------------------------
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=False
    )

    # --------------------------------------------------
    # 🚦 RATE LIMITER
    # --------------------------------------------------
    limiter.init_app(app)

    # --------------------------------------------------
    # 🧩 BLUEPRINTS
    # --------------------------------------------------
    app.register_blueprint(auth, url_prefix="/auth")

    # --------------------------------------------------
    # ❤️ HEALTH
    # --------------------------------------------------
    @app.route("/")
    def home():
        return {"msg": "EunaStudio Backend OK ✅"}

    @app.route("/health")
    def health():
        return {"status": "healthy"}

    return app

app = create_app()