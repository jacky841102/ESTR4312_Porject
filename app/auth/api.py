from flask import render_template, Blueprint, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, \
     check_password_hash
from .form import LoginForm
from app import db
from app.models import User
from . import auth, login_manager

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if not current_user.is_authenticated:
        form = LoginForm(request.form)
        if form.validate_on_submit():
            username = form.username.data
            password = generate_password_hash(form.password.data)
            db.session.add(User(username, password))
            db.session.commit()
            return 'register successfully'
        return render_template('signup.html', form=form)
    else:
        return 'hello %s' % current_user.username

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated:
        form = LoginForm(request.form)
        if form.validate_on_submit():
            user = User.query.filter(User.username == form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                return 'login successfully'
        return render_template('login.html', form=form)
    else:
        return 'hello %s' % current_user.username


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return 'logout'

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)
