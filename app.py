import logging
import os
from datetime import timedelta

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from utils.limiter import limiter

# 🔐 AUTH
from auth.auth_routes import auth

# 🔐 2FA / TOTP
from auth.totp_routes import totp_bp

# 📝 REGISTRO
from registro.registro_routes import registro

# 📊 HISTORY
from routes.history import history

# 💬 COMMENTS
from routes.comments import comments
from utils.db_init import init_comments_table

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

    JWTManager(app)

    # --------------------------------------------------
    # 🌍 CORS
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
    # 🧩 INIT DB TABLES
    # --------------------------------------------------
    try:
        init_comments_table()
    except Exception as e:
        print("❌ ERROR inicializando tabla comments:", e)

    # --------------------------------------------------
    # 🧩 BLUEPRINTS
    # --------------------------------------------------
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(totp_bp, url_prefix="/auth")
    app.register_blueprint(registro, url_prefix="/registro")
    app.register_blueprint(history, url_prefix="/history")
    app.register_blueprint(comments, url_prefix="/comments")

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