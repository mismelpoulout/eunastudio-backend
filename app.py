import logging
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

# ✅ IMPORTS MÍNIMOS (sin los que causan crash)
from utils.limiter import limiter
from auth.auth_routes import auth  # ← SOLO ESTE para /auth/user/status

logging.basicConfig(level=logging.INFO)

def create_app():
    app = Flask(__name__)

    # --------------------------------------------------
    # 🔐 CONFIG JWT (7 DÍAS - NO False)
    # --------------------------------------------------
    app.config["JWT_SECRET_KEY"] = os.environ.get(
        "JWT_SECRET_KEY", "dev-secret-no-usar-en-prod"
    )
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)  # ✅ FIJADO

    jwt = JWTManager(app)

    # --------------------------------------------------
    # 🌍 CORS LOCALHOST (ESPECÍFICO)
    # --------------------------------------------------
    CORS(
        app,
        origins=["http://localhost:3000"],  # ✅ NO "*"
        supports_credentials=True  # ✅ CRÍTICO
    )

    # --------------------------------------------------
    # 🚦 RATE LIMITER
    # --------------------------------------------------
    limiter.init_app(app)

    # --------------------------------------------------
    # 🧩 SOLO AUTH (lo esencial para sesión)
    # --------------------------------------------------
    app.register_blueprint(auth, url_prefix="/auth")  # ✅ /auth/user/status

    # --------------------------------------------------
    # ❤️ HEALTH CHECKS
    # --------------------------------------------------
    @app.route("/")
    def home():
        return {"msg": "EunaStudio Backend OK ✅"}

    @app.route("/health")
    def health():
        return {"status": "healthy", "auth": "ready"}

    return app

# 🔥 ENTRYPOINT
app = create_app()
