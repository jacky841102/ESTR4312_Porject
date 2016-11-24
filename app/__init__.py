from flask import Flask, render_template, send_from_directory
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CsrfProtect
import jinja2

def create_app():
    app = Flask(__name__)

    Bootstrap(app)

    my_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader('./effect/templates'),
        jinja2.FileSystemLoader('./auth/templates'),
        jinja2.FileSystemLoader('./album/templates')
    ])

    app.jinja_loader = my_loader

    app.config['BOOTSTRAP_SERVE_LOCAL'] = False

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/ierg4080'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.secret_key = 'super secret key'

    app.config.update(
        CELERY_BROKER_URL='amqp://guest@localhost//',
        CELERY_RESULT_BACKEND='redis://localhost',
        CELERY_BACKEND='redis://localhost'
    )

    CsrfProtect(app)
    app.config['UPLOAD_FOLDER'] = '/tmp/images'
    app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])
    return app

app = create_app()

db = SQLAlchemy(app)

from .auth import auth, login_manager
from .album import album
from .effect import effect
from .users import users
from .models import User, Following
from .worker import worker

app.register_blueprint(auth)
app.register_blueprint(album)
app.register_blueprint(effect)
app.register_blueprint(users)
login_manager.init_app(app)

# app.config['SERVER_NAME'] = 'localhost:5000'

db.create_all()

@app.route('/static/<path:path>')
def send_lib(path):
    print(path)
    return send_from_directory('static', path)

@app.route('/')
@login_required
def posts():
    user = User.query.get(current_user.id)
    photos = list(user.album)
    for following in user.followings:
        followed_id = following.followed_id
        followed = User.query.get(followed_id)
        for photo in followed.album:
            photos.append(photo)
    return render_template('list.jinja2', photos=sorted(photos, key=lambda x: x.submit_at, reverse=True))
