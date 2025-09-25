# app/main/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from . import main
from .. import db
from ..models import Paper   # ✅ import Paper model
from ..utils.decorators import admin_required
from ..forms import PaperUploadForm # ✅ import the upload form

@main.route("/")
def home():
    """Public home page"""
    return render_template("home.html")

@main.route("/dashboard")
@login_required
def dashboard():
    """Student dashboard - shows all papers with search, filter, and pagination"""

    # Get page number from request, default 1
    page = request.args.get("page", 1, type=int)

    # ✅ Ensure per_page is always >= 1
    per_page = request.args.get("per_page", 5, type=int)
    if per_page < 1:
        per_page = 5

    query = Paper.query  # start with all papers

    # Optional search and filter
    search = request.args.get("q")
    subject = request.args.get("subject")
    year = request.args.get("year")

    if search:
        query = query.filter(Paper.title.ilike(f"%{search}%"))
    if subject:
        query = query.filter(Paper.subject.ilike(f"%{subject}%"))
    if year:
        query = query.filter(Paper.year == year)

    # ✅ Paginate safely
    papers = query.order_by(Paper.uploaded_at.desc()).paginate(page=page, per_page=per_page)

    return render_template("dashboard.html", user=current_user, papers=papers)

# Upload route
@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Upload new past paper - uses Flask-WTF form (includes CSRF token)."""
    form = PaperUploadForm()
    if form.validate_on_submit():
        # form.file is a FileStorage
        uploaded = form.file.data
        filename = secure_filename(uploaded.filename)
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        uploaded.save(filepath)

        # Save to database
        new_paper = Paper(
            title=form.title.data,
            subject=form.subject.data,
            year=form.year.data or None,
            file_path=filepath,
            user_id=current_user.id
        )
        
        # Save to DB
        db.session.add(new_paper)
        db.session.commit()
        flash("Paper uploaded successfully!", "success")
        return redirect(url_for("main.dashboard"))

    # GET or invalid POST: render the page (form.hidden_tag() will include CSRF)
    return render_template("upload.html", form=form)

# Download route
@main.route("/download/<int:paper_id>")
@login_required
def download(paper_id):
    """Download an uploaded paper"""
    paper = Paper.query.get_or_404(paper_id)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(upload_folder, os.path.basename(paper.file_path), as_attachment=True)

# Preview route
@main.route("/preview/<int:paper_id>")
@login_required
def preview(paper_id):
    """Preview an uploaded paper (PDFs/images inline, others download)"""
    paper = Paper.query.get_or_404(paper_id)
    upload_folder = current_app.config["UPLOAD_FOLDER"]

    return send_from_directory(
        upload_folder,
        os.path.basename(paper.file_path),
        as_attachment=False  # 👈 lets browser preview if supported
    )

# Delete route
@main.route("/delete/<int:paper_id>", methods=["POST"])
@login_required
def delete_paper(paper_id):
    """Delete a paper (only by the owner)"""
    paper = Paper.query.get_or_404(paper_id)

    # Ensure the logged-in user owns this paper
    if paper.user_id != current_user.id:
        flash("You are not authorized to delete this file.", "danger")
        return redirect(url_for("main.dashboard"))

    # Delete file from disk if it exists
    if os.path.exists(paper.file_path):
        os.remove(paper.file_path)

    # Delete from database
    db.session.delete(paper)
    db.session.commit()

    flash("Paper deleted successfully!", "success")
    return redirect(url_for("main.dashboard"))


# 🔹 Search & filter for papers (global search)
@main.route("/papers")
def papers():
    """Search and filter past papers with pagination"""

    # Get query parameters from search form
    query = request.args.get("q")  # general search
    subject_filter = request.args.get("subject")
    year_filter = request.args.get("year")

    # Base query (start with all papers)
    papers_query = Paper.query

    # Apply filters dynamically
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

    # Pagination (6 per page)
    page = request.args.get("page", 1, type=int)
    results = papers_query.order_by(Paper.uploaded_at.desc()).paginate(page=page, per_page=6)

    return render_template("papers.html", papers=results)

# ✅ Import ConfirmForm for CSRF protection in delete forms
from app.forms import ConfirmForm

# User-specific papers view
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

    confirm_form = ConfirmForm()  # ✅ for CSRF in delete forms

    return render_template("my_papers.html", papers=papers, confirm_form=confirm_form)


# Dedicated paper view route
@main.route("/view/<int:paper_id>")
@login_required
def view_paper(paper_id):
    """Dedicated page to view a single paper with details + preview/download links"""
    paper = Paper.query.get_or_404(paper_id)
    return render_template("view_paper.html", paper=paper)


# @main.route("/admin/dashboard")
# @login_required
# @admin_required
# def admin_dashboard():
#     """Admin dashboard showing all uploaded papers"""
#     papers = Paper.query.order_by(Paper.uploaded_at.desc()).all()
#     return render_template("admin_dashboard.html", papers=papers)