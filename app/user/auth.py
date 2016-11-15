from flask import render_template, Blueprint, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, \
     check_password_hash
from .form import LoginForm


auth = Blueprint('auth', __name__, template_folder='templates')

db = SQLAlchemy()
login_manager = LoginManager()

class User(db.Model, UserMixin):
    # id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, primary_key=True)
    password = db.Column(db.String(255))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return "%s/%s" % (self.username, self.password)

    def get_id(self):
        return self.username

@auth.route('/signup', methods=['GET', 'POST'])
def register():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        username = form.username.data
        password = generate_password_hash(form.password.data)
        db.session.add(User(username, password))
        db.session.commit()
        return 'register successfully'
    return render_template('signup.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.get(form.username.data)
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            print(user)
            return 'login successfully'
    return render_template('login.html', form=form)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return 'logout'

@login_manager.user_loader
def load_user(username):
    return User.query.get(username)
