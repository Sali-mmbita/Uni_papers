# app/models.py
from . import db, bcrypt
from flask_login import UserMixin
from datetime import datetime
from flask import current_app
import os

# ------------------------------------------
# User model represents registered users
# ------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔹 New role field (default = "user", can also be "admin")
    role = db.Column(db.String(10), nullable=False, default="user")
    
    active = db.Column(db.Boolean, default=True)
    is_banned = db.Column(db.Boolean, default=False)
    
    # 🔹 Helper method to check if user is admin
    def is_admin(self):
        return self.role == "admin"
    
    # Relationship: one user can upload many papers
    papers = db.relationship("Paper", backref="author", lazy=True)

    # Hash password before storing
    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    # Verify hashed password
    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)


# ------------------------------------------
# Paper model represents uploaded past papers
# ------------------------------------------
class Paper(db.Model):
    __tablename__ = "papers"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(10), nullable=True)
    
    # 🔹 store only the filename, not the full path
    file_path = db.Column(db.String(200), nullable=False)   
    
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key: link paper to uploader
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # 🔹 Helper to get full path on disk
    def get_file_path(self):
        """Return the absolute path to the stored file"""
        upload_path = current_app.config["UPLOAD_PATH"]
        return os.path.join(upload_path, self.file_path)
