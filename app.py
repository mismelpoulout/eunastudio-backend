from utils.limiter import limiter
from auth.auth_routes import auth
from registro import registro
from routes.history import history  # 👈 IMPORTANTE

def create_app():
    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = os.environ.get(
        "JWT_SECRET_KEY", "dev-secret-no-usar-en-prod"
    )
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

    JWTManager(app)

    CORS(app, resources={r"/*": {"origins": "*"}})

    limiter.init_app(app)

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(registro, url_prefix="/registro")
    app.register_blueprint(history, url_prefix="/history")  # ✅ CLAVE

    @app.route("/")
    def home():
        return {"msg": "EunaStudio Backend OK ✅"}

    @app.route("/health")
    def health():
        return {"status": "healthy"}

    return app