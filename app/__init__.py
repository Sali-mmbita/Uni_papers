# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_migrate import Migrate
import os

# ------------------------------------------------
# Load environment variables from .env
# (like SECRET_KEY and DATABASE_URL)
# ------------------------------------------------
load_dotenv()

# ------------------------------------------------
# Initialize Flask extensions (but don't bind yet)
# ------------------------------------------------
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

# This sets where Flask-Login redirects users when login is required
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx"}

def create_app():
    """Factory function to create and configure the Flask app"""

    app = Flask(__name__)

    # ------------------------------------------------
    # App Configuration
    # ------------------------------------------------
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret_key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///site.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # File upload configuration
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # limit: 16MB

    # make sure uploads folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # ------------------------------------------------
    # Bind extensions to the app
    # ------------------------------------------------
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # ✅ Enable Flask-Migrate
    Migrate(app, db)

    # ------------------------------------------------
    # User loader function for Flask-Login
    # (import inside to avoid circular import issues)
    # ------------------------------------------------
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User  # import here instead of top

        return User.query.get(int(user_id))

    # ------------------------------------------------
    # Register Blueprints
    # ------------------------------------------------
    from .auth import auth as auth_blueprint
    from .main import main as main_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    return app
