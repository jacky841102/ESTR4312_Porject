from flask import render_template, request, redirect
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, \
     check_password_hash
from .form import LoginForm, SignupForm
from app import db
from app.models import User
from . import auth, login_manager

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm(request.form)
    if not current_user.is_authenticated:
        if form.validate_on_submit():
            username = form.username.data
            password = generate_password_hash(form.password.data)
            user = User(username, password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect('album')
    return render_template('signup.jinja2', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if not current_user.is_authenticated:
        if form.validate_on_submit():
            user = User.query.filter(User.username == form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect('album')
    return render_template('login.jinja2', form=form)

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('auth/login')

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)
