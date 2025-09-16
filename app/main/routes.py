# app/main/routes.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import main

# # Create the "main" blueprint
# main = Blueprint("main", __name__)

@main.route("/")
def home():
    """Public home page"""
    return render_template("home.html")

@main.route("/dashboard")
@login_required   # 🔒 Only accessible when logged in
def dashboard():
    """Student dashboard page"""
    return render_template("dashboard.html", user=current_user)
