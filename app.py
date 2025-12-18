import logging
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from utils.limiter import limiter
from admin.promo_routes import promo_bp
from auth.auth_routes import auth
from auth.totp_routes import totp_bp
from auth.password_routes import password_bp
from registro.registro_routes import registro

from payments.promo_routes import promo_bp
from payments.flow_routes import flow_bp

logging.basicConfig(level=logging.INFO)


def create_app():
    app = Flask(__name__)

    # --------------------------------------------------
    # 🔐 CONFIG JWT (PERSISTENCIA DE SESIÓN)
    # --------------------------------------------------
    app.config["JWT_SECRET_KEY"] = os.environ.get(
        "JWT_SECRET_KEY", "dev-secret-no-usar-en-prod"
    )


    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
    # 👆 el token NO expira automáticamente (persistencia total)
    # si prefieres expiración: timedelta(days=7)

    jwt = JWTManager(app)

    # --------------------------------------------------
    # 🌍 CORS GLOBAL
    # --------------------------------------------------
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=False,
    )

    # --------------------------------------------------
    # 🚦 RATE LIMITER
    # --------------------------------------------------
    limiter.init_app(app)

    # --------------------------------------------------
    # 🧩 BLUEPRINTS
    # --------------------------------------------------
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(totp_bp, url_prefix="/auth")
    app.register_blueprint(password_bp, url_prefix="/auth")
    app.register_blueprint(registro, url_prefix="/registro")
    app.register_blueprint(promo_bp, url_prefix="/payments")
    app.register_blueprint(flow_bp, url_prefix="/payments")
    app.register_blueprint(promo_bp)

    # --------------------------------------------------
    # ❤️ HEALTH CHECK
    # --------------------------------------------------
    @app.get("/")
    def home():
        return {"msg": "EunaStudio Backend OK"}

    return app


# 🔥 ENTRYPOINT (Gunicorn / local)
app = create_app()