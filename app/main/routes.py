# app/main/routes.py
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, send_from_directory, current_app
)
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from . import main
from .. import db
from ..models import Paper
from ..utils.decorators import admin_required
from ..forms import PaperUploadForm, ConfirmForm  # ✅ import forms

# -------------------------
# Helpers
# -------------------------
def is_allowed(filename):
    """Check if file extension is allowed based on config"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in current_app.config["UPLOAD_EXTENSIONS"]

# -------------------------
# Routes
# -------------------------

@main.route("/")
def home():
    """Public home page"""
    return render_template("home.html")

@main.route("/dashboard")
@login_required
def dashboard():
    """Student dashboard - shows all papers with search, filter, and pagination"""

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    if per_page < 1:
        per_page = 5

    query = Paper.query

    search = request.args.get("q")
    subject = request.args.get("subject")
    year = request.args.get("year")

    if search:
        query = query.filter(Paper.title.ilike(f"%{search}%"))
    if subject:
        query = query.filter(Paper.subject.ilike(f"%{subject}%"))
    if year:
        query = query.filter(Paper.year == year)

    papers = query.order_by(Paper.uploaded_at.desc()).paginate(page=page, per_page=per_page)

    return render_template("dashboard.html", user=current_user, papers=papers)


# -------------------------
# Upload
# -------------------------
@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Upload new past paper - uses Flask-WTF form (includes CSRF token)."""
    form = PaperUploadForm()
    if form.validate_on_submit():
        uploaded = form.file.data
        filename = secure_filename(uploaded.filename)

        if not filename or not is_allowed(filename):
            flash("Invalid file type. Only PDF and DOCX are allowed.", "danger")
            return redirect(request.url)

        upload_path = current_app.config["UPLOAD_PATH"]
        os.makedirs(upload_path, exist_ok=True)

        filepath = os.path.join(upload_path, filename)
        uploaded.save(filepath)

        # Save only filename in DB, not full path
        new_paper = Paper(
            title=form.title.data,
            subject=form.subject.data,
            year=form.year.data or None,
            file_path=filename,  # ✅ store only filename
            user_id=current_user.id
        )

        db.session.add(new_paper)
        db.session.commit()
        flash("Paper uploaded successfully!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("upload.html", form=form)


# -------------------------
# Download
# -------------------------
@main.route("/download/<int:paper_id>")
@login_required
def download(paper_id):
    """Download an uploaded paper"""
    paper = Paper.query.get_or_404(paper_id)
    upload_path = current_app.config["UPLOAD_PATH"]
    return send_from_directory(upload_path, paper.file_path, as_attachment=True)


# -------------------------
# Preview
# -------------------------
@main.route("/preview/<int:paper_id>")
@login_required
def preview(paper_id):
    """Preview an uploaded paper (PDFs/images inline, others download)"""
    paper = Paper.query.get_or_404(paper_id)
    upload_path = current_app.config["UPLOAD_PATH"]

    return send_from_directory(
        upload_path,
        paper.file_path,
        as_attachment=False
    )


# -------------------------
# Delete
# -------------------------
@main.route("/delete/<int:paper_id>", methods=["POST"])
@login_required
def delete_paper(paper_id):
    """Delete a paper (only by the owner)"""
    paper = Paper.query.get_or_404(paper_id)

    if paper.user_id != current_user.id:
        flash("You are not authorized to delete this file.", "danger")
        return redirect(url_for("main.dashboard"))

    upload_path = current_app.config["UPLOAD_PATH"]
    filepath = os.path.join(upload_path, paper.file_path)

    if os.path.exists(filepath):
        os.remove(filepath)

    db.session.delete(paper)
    db.session.commit()

    flash("Paper deleted successfully!", "success")
    return redirect(url_for("main.dashboard"))


# -------------------------
# Global search
# -------------------------
@main.route("/papers")
def papers():
    """Search and filter past papers with pagination"""

    query = request.args.get("q")
    subject_filter = request.args.get("subject")
    year_filter = request.args.get("year")

    papers_query = Paper.query

    if query:
        papers_query = papers_query.filter(
            (Paper.title.ilike(f"%{query}%")) |
            (Paper.subject.ilike(f"%{query}%")) |
            (Paper.year.ilike(f"%{query}%"))
        )
    if subject_filter:
        papers_query = papers_query.filter(Paper.subject.ilike(f"%{subject_filter}%"))
    if year_filter:
        papers_query = papers_query.filter(Paper.year == year_filter)

    page = request.args.get("page", 1, type=int)
    results = papers_query.order_by(Paper.uploaded_at.desc()).paginate(page=page, per_page=6)

    return render_template("papers.html", papers=results)


# -------------------------
# User-specific papers
# -------------------------
@main.route("/my_papers")
@login_required
def my_papers():
    """Show only the logged-in user's uploaded papers with pagination"""
    page = request.args.get("page", 1, type=int)
    papers = (
        Paper.query.filter_by(user_id=current_user.id)
        .order_by(Paper.uploaded_at.desc())
        .paginate(page=page, per_page=5)
    )

    confirm_form = ConfirmForm()
    return render_template("my_papers.html", papers=papers, confirm_form=confirm_form)


# -------------------------
# Dedicated paper view
# -------------------------
@main.route("/view/<int:paper_id>")
@login_required
def view_paper(paper_id):
    """Dedicated page to view a single paper with details + preview/download links"""
    paper = Paper.query.get_or_404(paper_id)
    return render_template("view_paper.html", paper=paper)
