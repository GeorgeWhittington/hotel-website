from datetime import date, timedelta

from sqlalchemy import or_, and_, not_
from flask import Blueprint, render_template, request, flash, redirect, url_for, session

from .models import Location, Booking, Room, Roomtype
from .forms import WhereToForm

bp = Blueprint("hotels", __name__)


@bp.route("/")
def home():
    form = WhereToForm()
    locations = Location.query.order_by(Location.name).all()
    form.location.choices = [(l.id, l.name) for l in locations]

    today = date.today()
    one_month = today + timedelta(days=30)

    return render_template(
        "hotels/home.html", form=form, locations=locations,
        today=today, one_month=one_month)


def test_booking_duration(booking_start, booking_end):
    """If the booking duration is invalid, returns True"""
    return (
        booking_start is None or
        booking_end is None or
        booking_start < date.today() or
        booking_end <= date.today() or
        booking_start > booking_end
    )


def test_guests(guests):
    """If the number of guests in invalid, returns True"""
    # Extract these values to a constants file?
    return guests < 1 or guests > 6


@bp.route("/search")
def search():
    form = WhereToForm()
    locations = Location.query.order_by(Location.name).all()
    location_ids = [l.id for l in locations]
    form.location.choices = [(l.id, l.name) for l in locations]

    location = request.args.get("location", type=int)
    booking_start = request.args.get("booking_start", type=date.fromisoformat)
    booking_end = request.args.get("booking_end", type=date.fromisoformat)
    guests = request.args.get("guests", 1, type=int)

    invalid = False

    if location not in location_ids:
        invalid = True
        location = None
    else:
        form.location.data = location

    if test_booking_duration(booking_start, booking_end):
        invalid = True
        booking_start = form.booking_start.data
        booking_end = form.booking_end.data
    else:
        form.booking_start.data = booking_start
        form.booking_end.data = booking_end

    if test_guests(guests):
        invalid = True
        guests = 1
    else:
        form.guests.data = guests

    # Save and retrieve from session
    if invalid:
        try:
            location = session["location"]
            booking_start = date.fromisoformat(session["booking_start"])
            booking_end = date.fromisoformat(session["booking_end"])
            guests = session["guests"]
        except KeyError:
            # No previous search to populate results with
            flash("Invalid search parameters")
            return redirect(url_for("hotels.home"))

        if (location not in location_ids or
                test_booking_duration(booking_start, booking_end) or
                test_guests(guests)):
            # Previous search is now invalid, cannot populate results with it
            flash("Invalid search parameters")
            return redirect(url_for("hotels.home"))
    else:
        session["location"] = location
        session["booking_start"] = booking_start.isoformat()
        session["booking_end"] = booking_end.isoformat()
        session["guests"] = guests

    # Logic for testing if there is any overlap of ranges comes from: https://stackoverflow.com/a/3269471
    results = Room.query.with_entities(Location.id, Roomtype.id)
    results = results.join(Room.location).join(Room.room_type).join(Room.bookings, isouter=True)
    results = results.where(
        Roomtype.max_occupants >= guests,
        or_(
            Booking.id == None,
            not_(and_(
                booking_start <= Booking.booking_end,
                Booking.booking_start <= booking_end
            ))  # !(x1 <= y2 AND y1 <= x2)
        )
    ).group_by(Roomtype.id, Location.id)

    if location:
        results = results.where(Location.id == location)

    results = results.all()

    locations = {l.id: l for l in locations}
    room_types = {rt.id: rt for rt in Roomtype.query.all()}

    results = [(locations[l_id], room_types[rt_id]) for l_id, rt_id in results]

    return render_template(
        "hotels/search.html", form=form, results=results,
        room_types={"S": "Standard", "D": "Double", "F": "Family"})


@bp.route("/search_submit", methods=["POST"])
def search_submit():
    form = WhereToForm(request.form)
    locations = Location.query.order_by(Location.name).all()
    form.location.choices = [(l.id, l.name) for l in locations]

    if form.validate_on_submit():
        # Verify booking dates are sensible
        if not (form.booking_start.data < date.today() or
                form.booking_end.data <= date.today() or
                form.booking_start.data > form.booking_end.data):
            form_data = {
                "location": form.location.data,
                "booking_start": form.booking_start.data,
                "booking_end": form.booking_end.data,
                "guests": form.guests.data
            }
            return redirect(url_for("hotels.search", **form_data))

    if (form.booking_start.data < date.today() or
            form.booking_end.data <= date.today() or
            form.booking_start.data > form.booking_end.data):
        flash("Please select a valid booking duration.")

    if form.location.errors:
        flash("Please select a location from the list provided.")

    referrer = request.referrer[8:]  # Cut off http/https prefix
    referrer_path = referrer[referrer.find("/"):]  # Slice by first / for the path
    if (query_ind := referrer_path.find("?")) != -1:
        # Slice by first ?, if there is one, to cut off url queries
        referrer_path = referrer_path[:query_ind]

    lookup = {
        "/": "hotels.home",
        "/search": "hotels.search"
    }

    print(referrer_path)

    return redirect(url_for(lookup.get(referrer_path, "hotels.home")))


@bp.route("/room")
def room():
    pass
