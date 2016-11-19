from flask import Blueprint
from flask_login import LoginManager

follow = Blueprint('follow', __name__, url_prefix='/follow', template_folder='templates')

from .api import *
