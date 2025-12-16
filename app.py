import logging
from flask import Flask
from flask_cors import CORS

#from auth.auth_routes import auth
#from registro.registro_routes import registro

# 👇 IMPORT LOCAL DIRECTO (CLAVE)
from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def home():
        return {"msg": "Servidor funcionando ✔"}

    return app

app = create_app()