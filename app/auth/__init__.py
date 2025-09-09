# app/auth/__init__.py

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import routes  # import routes after blueprint is created
