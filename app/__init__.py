from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/ierg4080'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'super secret key'


app.config['SERVER_NAME'] = 'localhost:8080'
app.config['UPLOAD_FOLDER'] = '/tmp/images'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

db = SQLAlchemy(app)

from .auth import auth, login_manager
from .album import album
from .effect import effect

app.register_blueprint(auth)
app.register_blueprint(album)
app.register_blueprint(effect)

login_manager.init_app(app)

# with app.app_context():
db.create_all()
