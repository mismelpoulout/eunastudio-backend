import os
from flask import Flask
from flask_cors import CORS

# Blueprints
from auth.auth_routes import auth
from registro.registro_routes import registro
from routes.debug import debug   # 👈 IMPORTANTE


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Registrar Blueprints
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(registro, url_prefix="/registro")

    # Debug: acceso a database.json en producción
    app.register_blueprint(debug)  # 👈 No lleva prefix: ya tiene /debug/users

    @app.get("/")
    def home():
        return {"msg": "Servidor funcionando ✔"}

    return app


app = create_app()


if __name__ == "__main__":
    # Render asigna dinámicamente el puerto
    port = int(os.environ.get("PORT", 5000))

    # Desarrollo local
    app.run(host="0.0.0.0", port=port, debug=True)
