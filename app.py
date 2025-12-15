import os
from flask import Flask
from flask_cors import CORS

# Blueprints
from auth.auth_routes import auth
from registro.registro_routes import registro


def create_app():
    app = Flask(__name__)

    # CORS (permitir frontend)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # ---------------------------
    # Registrar Blueprints
    # ---------------------------
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(registro, url_prefix="/registro")

    # ---------------------------
    # Health check
    # ---------------------------
    @app.get("/")
    def home():
        return {"msg": "Servidor funcionando ✔"}

    return app


# Crear app
app = create_app()


if __name__ == "__main__":
    # Railway asigna PORT automáticamente
    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )