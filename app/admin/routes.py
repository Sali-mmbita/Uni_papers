# app/admin/routes.py
from flask import render_template, request, url_for, redirect, flash, abort, current_app # ✅ import current_app
from flask_login import login_required, current_user # ✅ import current_user
from .. import db # ✅ import db
from ..models import User, Paper  # ✅ import User and Paper models
from . import admin # admin Blueprint
from ..utils.decorators import admin_required # ✅ import admin_required decorator
from ..forms import ConfirmForm  # ✅ import ConfirmForm

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

    # single ConfirmForm instance used to render CSRF token for every row's form
    confirm_form = ConfirmForm()

    return render_template("admin/admin_dashboard.html", users=users, papers=papers, confirm_form=confirm_form)


# All action routes validate CSRF by checking the form.validate_on_submit()
@admin.route("/promote/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def promote_user(user_id):
    form = ConfirmForm()
    if not form.validate_on_submit():
        flash("Invalid request (CSRF).", "danger")
        return redirect(url_for("admin.dashboard"))

    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        flash(f"{user.username} is already an admin.", "info")
        return redirect(url_for("admin.dashboard"))

    user.role = "admin"
    db.session.commit()
    flash(f"{user.username} has been promoted to admin.", "success")
    return redirect(url_for("admin.dashboard"))


@admin.route("/demote/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def demote_user(user_id):
    form = ConfirmForm()
    if not form.validate_on_submit():
        flash("Invalid request (CSRF).", "danger")
        return redirect(url_for("admin.dashboard"))

    user = User.query.get_or_404(user_id)
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

# Ban user
@admin.route("/ban_user/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def ban_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        flash("You cannot ban another admin.", "danger")
        return redirect(url_for("admin.admin_dashboard"))
    user.is_banned = True
    db.session.commit()
    flash(f"User {user.username} has been banned.", "success")
    return redirect(url_for("admin.admin_dashboard"))


# Unban user
@admin.route("/unban_user/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def unban_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    db.session.commit()
    flash(f"User {user.username} has been unbanned.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin.route("/delete_user/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    form = ConfirmForm()
    if not form.validate_on_submit():
        flash("Invalid request (CSRF).", "danger")
        return redirect(url_for("admin.dashboard"))

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("admin.dashboard"))

    papers = Paper.query.filter_by(user_id=user.id).all()
    for p in papers:
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


@admin.route("/delete_paper/<int:paper_id>", methods=["POST"])
@login_required
@admin_required
def delete_paper_admin(paper_id):
    form = ConfirmForm()
    if not form.validate_on_submit():
        flash("Invalid request (CSRF).", "danger")
        return redirect(url_for("admin.dashboard"))

    paper = Paper.query.get_or_404(paper_id)
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
