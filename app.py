import logging
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

from utils.limiter import limiter
from admin.promo_routes import promo_bp
from auth.auth_routes import auth
from auth.totp_routes import totp_bp
from auth.password_routes import password_bp
from registro.registro_routes import registro
from payments.flow_routes import flow_bp  # ← FIJO: Solo uno

logging.basicConfig(level=logging.INFO)

def create_app():
    app = Flask(__name__)

    # --------------------------------------------------
    # 🔐 CONFIG JWT (✅ 7 DÍAS PERSISTENCIA)
    # --------------------------------------------------
    app.config["JWT_SECRET_KEY"] = os.environ.get(
        "JWT_SECRET_KEY", "dev-secret-no-usar-en-prod"
    )
    
    # ✅ CAMBIAR A 7 DÍAS (NO False)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

    jwt = JWTManager(app)

    # --------------------------------------------------
    # 🌍 CORS CORREGIDO (LOCAL + PROD)
    # --------------------------------------------------
    CORS(
        app,
        origins=["http://localhost:3000", "https://eunastudio.up.railway.app"],  # ← ESPECÍFICO
        supports_credentials=True,  # ← CRÍTICO para cookies/JWT
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # --------------------------------------------------
    # 🚦 RATE LIMITER
    # --------------------------------------------------
    limiter.init_app(app)

    # --------------------------------------------------
    # 🧩 BLUEPRINTS (FIJADOS)
    # --------------------------------------------------
    app.register_blueprint(auth, url_prefix="/auth")           # ✅ /auth/user/status
    app.register_blueprint(totp_bp, url_prefix="/auth")       # ✅ /auth/totp/...
    app.register_blueprint(password_bp, url_prefix="/auth")   # ✅ /auth/password/...
    app.register_blueprint(registro, url_prefix="/registro")  # ✅ /registro/...
    
    # ✅ SOLO UN promo_bp (admin)
    app.register_blueprint(promo_bp, url_prefix="/admin/promo")
    
    # ✅ Payments
    app.register_blueprint(flow_bp, url_prefix="/payments")

    # --------------------------------------------------
    # ❤️ HEALTH CHECK
    # --------------------------------------------------
    @app.route("/")
    def home():
        return {"msg": "EunaStudio Backend OK"}

    return app

# 🔥 ENTRYPOINT
app = create_app()
