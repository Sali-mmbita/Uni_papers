# app/admin/routes.py
from flask import render_template, request, url_for, redirect, flash, abort
from flask_login import login_required, current_user
from .. import db
from ..models import User, Paper
from . import admin
from ..utils.decorators import admin_required

# Admin dashboard: list users & papers (paginated)
@admin.route("/dashboard")
@login_required
@admin_required
def dashboard():
    # pagination params
    user_page = request.args.get("user_page", 1, type=int)
    paper_page = request.args.get("paper_page", 1, type=int)
    per_page = 10

    users = User.query.order_by(User.id.asc()).paginate(page=user_page, per_page=per_page)
    papers = Paper.query.order_by(Paper.uploaded_at.desc()).paginate(page=paper_page, per_page=per_page)

    return render_template("admin/admin_dashboard.html", users=users, papers=papers)

# Promote user to admin (POST)
@admin.route("/promote/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def promote_user(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent demoting/promoting the last admin by mistake (simple check)
    if user.role == "admin":
        flash(f"{user.username} is already an admin.", "info")
        return redirect(url_for("admin.dashboard"))

    user.role = "admin"
    db.session.commit()
    flash(f"{user.username} has been promoted to admin.", "success")
    return redirect(url_for("admin.dashboard"))

# Demote admin back to user (POST)
@admin.route("/demote/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def demote_user(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent self-demotion
    if user.id == current_user.id:
        flash("You cannot demote yourself.", "danger")
        return redirect(url_for("admin.dashboard"))

    if user.role != "admin":
        flash(f"{user.username} is not an admin.", "info")
        return redirect(url_for("admin.dashboard"))

    user.role = "user"
    db.session.commit()
    flash(f"{user.username} has been demoted to user.", "success")
    return redirect(url_for("admin.dashboard"))

# Delete a user (POST)
@admin.route("/delete_user/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent deleting self
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("admin.dashboard"))

    # optional: delete this user's papers too (and files)
    papers = Paper.query.filter_by(user_id=user.id).all()
    for p in papers:
        # attempt to remove file from disk (if you want)
        try:
            import os
            if p.file_path and os.path.exists(p.file_path):
                os.remove(p.file_path)
        except Exception:
            pass
        db.session.delete(p)

    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.username} and their papers have been deleted.", "success")
    return redirect(url_for("admin.dashboard"))

# Delete a paper (POST)
@admin.route("/delete_paper/<int:paper_id>", methods=["POST"])
@login_required
@admin_required
def delete_paper_admin(paper_id):
    paper = Paper.query.get_or_404(paper_id)

    # remove file from disk
    try:
        import os
        if paper.file_path and os.path.exists(paper.file_path):
            os.remove(paper.file_path)
    except Exception:
        pass

    db.session.delete(paper)
    db.session.commit()
    flash("Paper deleted successfully.", "success")
    return redirect(url_for("admin.dashboard"))
