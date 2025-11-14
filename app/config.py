# app/config.py
import os

class Config:
    """Base configuration shared by all environments."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File Upload Security
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

    # Flask Security Hardening
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

    # CSRF
    WTF_CSRF_TIME_LIMIT = None  # CSRF token never expires

    # Allow only safe extensions
    ALLOWED_EXTENSIONS = {"pdf", "docx"}

class DevelopmentConfig(Config):
    """Config for local development."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URI", "sqlite:///site.db")

class ProductionConfig(Config):
    """Config for production deployment."""
    DEBUG = False

    # Use PostgreSQL in production (Render, Railway)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    # Secure cookies for HTTPS deployments
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
