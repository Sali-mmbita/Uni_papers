# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_mailman import Mail
# from flask_wtf import CSRFProtect
import os

load_dotenv()

# Initialize extensions (not yet bound to app)
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
# csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

# File upload configuration
BASE_DIR = os.getcwd()
UPLOAD_PATH = os.path.join(BASE_DIR, "uploads", "papers")
ALLOWED_EXTENSIONS = [".pdf", ".docx"]

def create_app():
    app = Flask(__name__)

    # Core settings
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret_key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///site.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Upload settings
    app.config["UPLOAD_PATH"] = UPLOAD_PATH
    app.config["UPLOAD_EXTENSIONS"] = ALLOWED_EXTENSIONS
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
    os.makedirs(UPLOAD_PATH, exist_ok=True)

    # Mail settings
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")
    app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASS")

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    # csrf.init_app(app)

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    # Register blueprints
    from .auth import auth as auth_blueprint
    from .main import main as main_blueprint
    from .admin import admin as admin_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint, url_prefix="/admin")

    return app
