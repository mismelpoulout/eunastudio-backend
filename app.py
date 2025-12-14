import os
from flask import Flask
from flask_cors import CORS

# Blueprints
from auth.auth_routes import auth
from registro.registro_routes import registro
from routes.debug import debug  # 👈 importante para /debug/users
from routes.debug_db import debug_db
app.register_blueprint(debug_db)

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Registrar Blueprints
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(registro, url_prefix="/registro")

    # Debug: ver contenido de database.json
    # /debug/users → lista todos los usuarios guardados
    app.register_blueprint(debug)

    @app.get("/")
    def home():
        return {"msg": "Servidor funcionando ✔"}

    return app


app = create_app()


if __name__ == "__main__":
    # Render asigna dinámicamente el puerto en la variable PORT
    port = int(os.environ.get("PORT", 5000))

    # Ejecutar localmente con debug
    app.run(host="0.0.0.0", port=port, debug=True)