from flask import Blueprint


index_blu = Blueprint('', __name__)

from . import views
