from flask import Blueprint, redirect, url_for, flash
from flask.templating import render_template
from flask_login import LoginManager, login_manager, login_required
from flask_login.utils import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError

from .models import db, User
from .forms import UsernamePasswordForm

bp = Blueprint("auth", __name__)
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = UsernamePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Logged in.")

                return redirect(url_for("hotels.home"))
        
        flash("The username or password you have entered is invalid.")
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect("/")


# Based on: https://flask.palletsprojects.com/en/2.0.x/tutorial/views/
@bp.route("/register", methods=("GET", "POST"))
def register():
    form = UsernamePasswordForm()

    if form.validate_on_submit():
        try:
            # Specifying exact hash parameters incase the default changes
            user = User(
                username=form.username.data,
                password=generate_password_hash(
                    form.password.data,
                    method="pbkdf2:sha256:150000",
                    salt_length=16))

            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            flash(f"The user {form.username.data} is already registered.")
        else:
            return redirect(url_for("auth.login"))
    
    return render_template("auth/register.html", form=form)


@bp.route("/my-account")
@login_required
def my_account():
    return render_template("auth/my_account.html")