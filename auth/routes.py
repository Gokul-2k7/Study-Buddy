from main import bcrypt,db
from flask import render_template, request, redirect, url_for,Blueprint,flash
from models import User
from forms import LoginForm,RegisterForm
from flask_login import login_required, login_user, logout_user

auth=Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        user=User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            if request.args.get('next'):
                return redirect(request.args.get('next'))
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))