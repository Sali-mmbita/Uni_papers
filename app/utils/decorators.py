# app/utils/decorators.py
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    """
    Decorator to ensure the current_user is authenticated and an admin.
    Usage: @login_required @admin_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_admin", lambda: False)():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
