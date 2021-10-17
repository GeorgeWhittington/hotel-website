from typing import Optional

from flask import Blueprint, request, redirect, url_for, flash
import flask
from flask.templating import render_template
from flask_login import LoginManager, UserMixin, login_manager, login_required
from flask_login.utils import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector

from .db import get_db
from .forms import UsernamePasswordForm

bp = Blueprint("auth", __name__)
login_manager = LoginManager()


class User(UserMixin):
    """User class, for ease of use with the flask-login plugin"""

    def __init__(self, id: str, username: str, admin: bool) -> None:
        super().__init__()

        self.id = id
        self.username = username
        self.admin = admin

    @staticmethod
    def get(user_id: str) -> Optional["User"]:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT id, username, admin FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return User(*row)
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional["User"]:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT id, username, password, admin FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()

        if not row:
            return None

        if not check_password_hash(row["password"], password):
            return None
        
        return User(row["id"], row["username"], row["admin"])


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = UsernamePasswordForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            login_user(user)
            flash("Logged in.")

            return redirect(flask.url_for("hotels.home"))
        
        flash("The username or password you have entered is invalid.")
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


# Based on: https://flask.palletsprojects.com/en/2.0.x/tutorial/views/
@bp.route("/register", methods=("GET", "POST"))
def register():
    form = UsernamePasswordForm()

    if form.validate_on_submit():
        db = get_db()
        try:
            # Specifying exact hash parameters incase the default changes
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (form.username.data, generate_password_hash(form.password.data, method="pbkdf2:sha256:150000", salt_length=16))
            )
            db.commit()
        except mysql.connector.IntegrityError:
            flash(f"The user {form.username.data} is already registered.")
        else:
            return redirect(url_for("auth.login"))
    
    return render_template("auth/register.html", form=form)
