from flask import Blueprint
effect = Blueprint('effect', __name__, url_prefix='/effect', template_folder='templates')

from .api import *
