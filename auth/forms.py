from wtforms import Form, StringField, PasswordField, ValidationError, validators,SubmitField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from main import db,bcrypt
from models import User
class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    submit=SubmitField('Submit')
    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError('Username does not exist. Please register first.')
        
    def validate_password(self,password):
        user=User.query.filter_by(username=self.username.data).first()
        if user and not bcrypt.check_password_hash(user.password, password.data):
            raise ValidationError('Incorrect password. Please try again.')
        
class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])
    confirm = PasswordField('Confirm Password', [validators.DataRequired(), validators.EqualTo('password', message='Passwords must match')])
    profile_image = FileField('Profile Image', [FileAllowed(['jpg', 'png'], 'Images only!')],default='default.jpg')
    submit=SubmitField('Submit')
    
    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists. Please choose a different one.')
        
    def validate_email(self,email):
        user=User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already exists. Please choose a different one.')