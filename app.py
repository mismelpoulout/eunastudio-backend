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

from timers.time_routes import time_bp

# 🧠 EXAMS (IA)
from routes.exams import exams_bp

logging.basicConfig(level=logging.INFO)


def create_app():
    app = Flask(__name__)

    # --------------------------------------------------
    # 🔐 JWT CONFIG (FIJO Y CONSISTENTE)
    # --------------------------------------------------
    app.config["JWT_SECRET_KEY"] = "EUNASTUDIO_SUPER_SECRET_JWT_KEY_2025"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"

    JWTManager(app)

@jwt.invalid_token_loader
def invalid_token_callback(error):
    logging.error(f"❌ JWT inválido: {error}")
    return {"msg": "Invalid token"}, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    logging.error(f"❌ JWT faltante: {error}")
    return {"msg": "Missing Authorization Header"}, 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    logging.error("❌ JWT expirado")
    return {"msg": "Token expired"}, 401

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
    app.register_blueprint(exams_bp, url_prefix="/exam")
    app.register_blueprint(time_bp, url_prefix="/metrics")

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