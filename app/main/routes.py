# app/main/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from . import main
from .. import db
from ..models import Paper   # ✅ import Paper model

@main.route("/")
def home():
    """Public home page"""
    return render_template("home.html")

@main.route("/dashboard")
@login_required
def dashboard():
    """Student dashboard page"""
    papers = Paper.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", user=current_user, papers=papers)

@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Upload new past paper"""
    if request.method == "POST":
        title = request.form.get("title")
        subject = request.form.get("subject")
        year = request.form.get("year")
        file = request.files["file"]

        if not file:
            flash("No file selected!", "danger")
            return redirect(url_for("main.upload"))

        # Secure filename
        filename = secure_filename(file.filename)
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # ✅ FIX: use file_path instead of filename
        new_paper = Paper(
            title=title,
            subject=subject,
            year=year,
            file_path=filepath,   # matches your model
            user_id=current_user.id
        )

        db.session.add(new_paper)
        db.session.commit()

        flash("Paper uploaded successfully!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("upload.html")

@main.route("/download/<int:paper_id>")
@login_required
def download(paper_id):
    """Download an uploaded paper"""
    paper = Paper.query.get_or_404(paper_id)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(upload_folder, os.path.basename(paper.file_path), as_attachment=True)

# preview route to view PDFs/images inline

@main.route("/preview/<int:paper_id>")
@login_required
def preview(paper_id):
    """Preview an uploaded paper (PDFs/images inline, others will download)"""
    paper = Paper.query.get_or_404(paper_id)
    upload_folder = current_app.config["UPLOAD_FOLDER"]

    return send_from_directory(
        upload_folder,
        os.path.basename(paper.file_path),
        as_attachment=False  # 👈 lets browser preview if supported
    )

# Delete route to remove a paper

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

# 🔹 Search & filter for papers
@main.route("/papers")
def papers():
    """Search and filter past papers"""

    # Get query parameters from search form
    search_query = request.args.get("q")  # general search
    subject_filter = request.args.get("subject")
    year_filter = request.args.get("year")

    # Base query (start with all papers)
    query = Paper.query

    # Apply filters dynamically
    if search_query:
        query = query.filter(Paper.title.ilike(f"%{search_query}%"))
    if subject_filter:
        query = query.filter(Paper.subject.ilike(f"%{subject_filter}%"))
    if year_filter:
        query = query.filter(Paper.year == year_filter)

    # Execute query
    results = query.order_by(Paper.uploaded_at.desc()).all()
    
    return render_template("papers.html", papers=results)

    

# View all papers uploaded by the logged-in user
@main.route("/my_papers")
@login_required
def my_papers():
    """Show all papers uploaded by the current user"""
    papers = Paper.query.filter_by(user_id=current_user.id).order_by(Paper.uploaded_at.desc()).all()
    return render_template("my_papers.html", papers=papers)

# View a single paper's details
@main.route("/view/<int:paper_id>")
@login_required
def view_paper(paper_id):
    """Dedicated page to view a single paper with details + preview/download links"""
    paper = Paper.query.get_or_404(paper_id)
    return render_template("view_paper.html", paper=paper)
