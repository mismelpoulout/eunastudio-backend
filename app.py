import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

from auth.auth_routes import auth
from auth.totp_routes import totp_bp
from registro.registro_routes import registro

logging.basicConfig(level=logging.INFO)

def create_app():
    app = Flask(__name__)

    # 🔥 CORS GLOBAL REAL
    CORS(
        app,
        origins="*",
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        supports_credentials=False,
    )

    # 🔥 INTERCEPTAR PREFLIGHT ANTES DE TODO
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({"msg": "OK"})
            response.status_code = 200
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response

    # Blueprints
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(totp_bp, url_prefix="/auth")
    app.register_blueprint(registro, url_prefix="/registro")

    @app.route("/", methods=["GET"])
    def home():
        return {"msg": "EunaStudio Backend OK"}

    return app


app = create_app()