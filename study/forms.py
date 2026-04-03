from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField

class UploadForm(FlaskForm):
    file = FileField('Upload Document', validators=[FileAllowed(['pdf', 'docx', 'txt'], 'Documents only!')])
    text= 
    submit = SubmitField('Upload')