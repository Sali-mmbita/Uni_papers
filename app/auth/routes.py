# app/auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .. import db, bcrypt
from ..models import User
from .forms import LoginForm, RegistrationForm
from . import auth
 
# Create the blueprint for authentication
# auth = Blueprint("auth", __name__)


# ---------------------------
# 🔹 Register Route
# ---------------------------
@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))  # redirect if already logged in

    form = RegistrationForm()
    if form.validate_on_submit():
        # Hash the password
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        # Create new user instance
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_pw,
            role=form.role.data   # ✅ save role from form
        )

        # Save user to database
        db.session.add(user)
        db.session.commit()

        # ✅ Flash success message after registration
        flash("Account created successfully! You can now log in.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


# ---------------------------
# 🔹 Login Route
# ---------------------------
@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        # Check if user exists
        user = User.query.filter_by(email=form.email.data).first()

        # Verify password
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)

            # ✅ Flash success message after login
            flash(f"Welcome back, {user.username}!", "success")

            # Redirect to next page (if any), else dashboard
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.dashboard"))
        else:
            # ✅ Flash error message on invalid login
            flash("Invalid username or password. Please try again.", "danger")

    return render_template("login.html", form=form)


# ---------------------------
# 🔹 Logout Route
# ---------------------------
@auth.route("/logout")
@login_required
def logout():
    logout_user()

    # ✅ Flash logout message
    flash("You have been logged out successfully.", "info")

    return redirect(url_for("main.home"))
