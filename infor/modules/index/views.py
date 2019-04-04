from . import index_blu
from flask import current_app


@index_blu.route('/')
def index():
    return 'index'
