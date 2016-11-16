from flask import Blueprint
from flask_login import LoginManager

auth = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')
login_manager = LoginManager()

from .api import *
