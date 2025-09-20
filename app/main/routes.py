# app/main/routes.py
# from flask import Blueprint, render_template
# from flask_login import login_required, current_user
# from . import main

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from . import main
from .forms import UploadPaperForm
from ..models import Paper, db

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

# The file upload folder
@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload_paper():
    form = UploadPaperForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)  # clean filename
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # save paper info in DB
        paper = Paper(
            title=form.title.data,
            subject=form.subject.data,
            year=form.year.data,
            file_path=filename,
            uploader=current_user
        )
        db.session.add(paper)
        db.session.commit()

        flash("Paper uploaded successfully!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("upload.html", form=form)


@main.route("/uploads/<filename>")
@login_required
def download_file(filename):
    """Serve uploaded files securely"""
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)