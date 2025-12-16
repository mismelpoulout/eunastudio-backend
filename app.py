import faulthandler
import sys
import time

# 🔥 Esto hará que si se cuelga, imprima el stack trace en logs
faulthandler.enable()
faulthandler.dump_traceback_later(25, repeat=True, file=sys.stderr)

from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.get("/")
    def home():
        return {"msg": "Servidor funcionando ✔"}

    return app

app = create_app()