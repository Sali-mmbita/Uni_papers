# app/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Optional, Length, Email, EqualTo

# ----------------------------------------------------------
# Form for uploading past papers
class PaperUploadForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    subject = StringField("Subject", validators=[DataRequired(), Length(max=100)])
    year = StringField("Year", validators=[Optional(), Length(max=10)])
    file = FileField("Paper file", validators=[
        FileRequired(),
        FileAllowed(["pdf", "docx"], "PDF or DOCX only")
    ])
    submit = SubmitField("Upload")

# ----------------------------------------------------------
# Simple confirmation form for admin actions
class ConfirmForm(FlaskForm):
    """
    Small empty form used only for CSRF protection on action buttons
    (promote/demote/delete). The form's hidden_tag() carries the CSRF token.
    """
    submit = SubmitField("Confirm")
    
# ----------------------------------------------------------
# Forms for user registration and login
class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

# ----------------------------------------------------------
# Form for resetting password
class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm New Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Reset Password")