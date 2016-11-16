from flask import Blueprint
album = Blueprint('album', __name__, url_prefix='/album', template_folder='templates')

from .api import *
