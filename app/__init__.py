# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mailman import Mail
from datetime import timedelta
from flask_wtf.csrf import CSRFError
from dotenv import load_dotenv
import os

# Configs
from .config import DevelopmentConfig, ProductionConfig

load_dotenv()

# Initialize extensions (not yet bound to app)
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()

# Flask-Login settings
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

# File upload configuration
BASE_DIR = os.getcwd()
UPLOAD_PATH = os.path.join(BASE_DIR, "uploads", "papers")
ALLOWED_EXTENSIONS = [".pdf", ".docx"]

def create_app(config_class=None):
    """Flask application factory."""
    app = Flask(__name__)

    # Load config
    if config_class:
        app.config.from_object(config_class)
    else:
        env = os.getenv("FLASK_ENV", "development")
        if env == "production":
            app.config.from_object(ProductionConfig)
        else:
            app.config.from_object(DevelopmentConfig)

    # Upload settings
    app.config["UPLOAD_PATH"] = UPLOAD_PATH
    app.config["UPLOAD_EXTENSIONS"] = ALLOWED_EXTENSIONS
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
    os.makedirs(app.config["UPLOAD_PATH"], exist_ok=True)

    # Mail settings
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")
    app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASS")
    app.config["MAIL_BACKEND"] = "console"

    # Security & session settings
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = True        # requires HTTPS
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True
    app.config["REMEMBER_COOKIE_SECURE"] = True       # requires HTTPS
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

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

    # CSRF error handler
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        from flask import render_template, flash
        flash("Your session expired or the form was invalid. Please try again.", "danger")
        return render_template("errors/403.html"), 403

    return app
