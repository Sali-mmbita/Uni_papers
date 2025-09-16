# app/models.py
from . import db, bcrypt
from flask_login import UserMixin
from datetime import datetime

# User model represents registered users in DB
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Hash password before storing
    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    # Verify hashed password
    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)
