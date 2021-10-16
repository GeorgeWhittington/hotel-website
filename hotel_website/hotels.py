from flask import Blueprint

bp = Blueprint("hotels", __name__)


@bp.route("/")
def home():
    """Homepage, 'Where To?' widget, destination carousel, etc etc"""
    pass


@bp.route("/search")
def search():
    """Filter page for any hotel queries. Still deciding if this is going to be all server side or served by AJAX calls"""
    pass