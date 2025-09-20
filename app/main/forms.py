# app/main/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired

class UploadPaperForm(FlaskForm):
    title = StringField("Paper Title", validators=[DataRequired()])
    subject = StringField("Subject", validators=[DataRequired()])
    year = StringField("Year")
    file = FileField("Upload File", validators=[DataRequired()])
    submit = SubmitField("Upload")
