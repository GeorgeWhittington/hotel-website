from datetime import date

from flask import Blueprint, redirect, url_for, flash, request
from flask.templating import render_template
from flask_login import LoginManager, login_required, current_user
from flask_login.utils import login_user, logout_user
from werkzeug.security import check_password_hash

from .constants import ROOM_TYPES
from .forms import UsernamePasswordForm, UsernamePasswordUpdateForm
from .models import db, User, Booking

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
        if User.query.filter_by(username=form.username.data).first():
            flash(f"The username {form.username.data} is taken.")
        else:
            db.session.add(User.create_user(
                username=form.username.data,
                raw_password=form.password.data))
            db.session.commit()

            flash("Registered.")
            return redirect(url_for("auth.login"))

    if request.method == "POST" and form.username.errors:
        flash("Your username cannot be longer than 20 characters.")

    return render_template("auth/register.html", form=form)


@bp.route("/my-account", methods=["GET", "POST"])
@login_required
def my_account():
    bookings = Booking.query.where(
        Booking.user == current_user,
        Booking.booking_end >= date.today()
    ).all()

    form = UsernamePasswordUpdateForm()

    if not form.username.data:
        form.username.data = current_user.username

    if request.method == "POST":
        if form.validate_on_submit():
            change = False
            if current_user.username != form.username.data:
                if User.query.filter_by(username=form.username.data).first():
                    flash(f"The username {form.username.data} is taken.")
                    return render_template(
                        "auth/my_account.html", bookings=bookings,
                        ROOM_TYPES=ROOM_TYPES, form=form)
                else:
                    current_user.username = form.username.data
                    change = True

            if form.password.data:
                current_user.update_password(form.password.data)
                change = True

            if change:
                db.session.add(current_user)
                db.session.commit()
                flash("Account updated!")

        if form.username.errors:
            flash("Your username cannot be longer than 20 characters.")

    return render_template(
        "auth/my_account.html", bookings=bookings, ROOM_TYPES=ROOM_TYPES,
        form=form)
