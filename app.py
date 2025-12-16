from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.route("/")
    def home():
        return {"msg": "Servidor funcionando ✔"}

    return app

app = create_app()