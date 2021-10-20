from flask import Blueprint, render_template, request, flash

from .models import Location
from .forms import WhereToForm

bp = Blueprint("hotels", __name__)


@bp.route("/", methods=["GET", "POST"])
def home():
    """Homepage, 'Where To?' widget, destination carousel, etc etc"""
    locations = Location.query.order_by(Location.name).all()
    location_tuples = [(l.id, l.name) for l in locations]

    form = WhereToForm()
    form.location.choices = location_tuples

    if form.validate_on_submit():
        pass

    if request.method == "POST" and form.location.errors:
        flash("Please select a location from the list provided.")

    return render_template("hotels/home.html", form=form)


@bp.route("/search")
def search():
    """Filter page for any hotel queries. Still deciding if this is going to be all server side or served by AJAX calls"""
    pass
