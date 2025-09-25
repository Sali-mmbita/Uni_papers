# app/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class PaperUploadForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    subject = StringField("Subject", validators=[DataRequired(), Length(max=100)])
    year = StringField("Year", validators=[Optional(), Length(max=10)])
    file = FileField("Paper file", validators=[
        FileRequired(),
        FileAllowed(["pdf", "docx"], "PDF or DOCX only")
    ])
    submit = SubmitField("Upload")

class ConfirmForm(FlaskForm):
    """
    Small empty form used only for CSRF protection on action buttons
    (promote/demote/delete). The form's hidden_tag() carries the CSRF token.
    """
    submit = SubmitField("Confirm")
