from flask import Blueprint
from flask_login import LoginManager, login_manager

from .db import User

bp = Blueprint("auth", __name__, url_prefix="/auth")
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@bp.route("/login")
def login():
    pass


@bp.route("/logout")
def logout():
    pass


@bp.route("/signout")
def signout():
    pass