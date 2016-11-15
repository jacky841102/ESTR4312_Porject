from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .user.auth import auth, db, User, login_manager

app = Flask(__name__)
app.register_blueprint(auth)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/ierg4080'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'super secret key'

db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()
