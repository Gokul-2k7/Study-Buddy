from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view='auth.login'
app.config['SECRET_KEY']='your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
db=SQLAlchemy(app)

if "__main__" == __name__:   
    app.run(debug=True,port=5000)