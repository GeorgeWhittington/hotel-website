from datetime import date, timedelta
import calendar

from sqlalchemy import or_, and_, not_, func, text
from flask import Blueprint, render_template, request, flash, redirect, url_for, session

from .models import db, Location, Booking, Room, Roomtype, Currency
from .forms import WhereToForm
from .constants import MAX_GUESTS, CURRENCY_SYMBOLS


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
    """If the number of guests is invalid, returns True"""
    return guests < 1 or guests > MAX_GUESTS


bp = Blueprint("hotels", __name__)


@bp.route("/")
def home():
    form = WhereToForm()
    locations = Location.query.order_by(Location.name).all()
    form.location.choices = [(l.id, l.name) for l in locations]

    today = date.today()
    next_week = today + timedelta(days=7)

    next_month = today.replace(day=1) + timedelta(days=32)
    last_day = calendar.monthrange(next_month.year, next_month.month)[1]
    start_date = date(next_month.year, next_month.month, 1)
    end_date = date(next_month.year, next_month.month, last_day)

    top_5 = db.session.query(Location, func.count(Booking.id).label("total_bookings"))
    top_5 = top_5.join(Location.rooms).outerjoin(Room.bookings)
    top_5 = top_5.group_by(Location).order_by(text("total_bookings DESC"))
    top_5 = top_5.order_by(Location.name).limit(5).all()
    top_5 = [location for location, _ in top_5]

    return render_template(
        "hotels/home.html", form=form, locations=top_5,
        start_date=start_date, end_date=end_date,
        today=today.isoformat(), next_week=next_week.isoformat())


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

    rooms = []
    for l_id, rt_id in results:
        location = locations[l_id]
        room_type = room_types[rt_id]

        currency_acronym = request.cookies.get("current_currency", default="GBP")
        currency = Currency.query.filter_by(acronym=currency_acronym).first()

        symbol = CURRENCY_SYMBOLS[currency_acronym]

        price, discount_price = location.find_room_prices(
            room_type=room_type, booking_start=booking_start,
            booking_end=booking_end, currency=currency, guests=guests)

        rooms.append((location, room_type, price, discount_price, symbol))

    return render_template(
        "hotels/search.html", form=form, results=rooms,
        room_types={"S": "Standard", "D": "Double", "F": "Family"},
        booking_start=booking_start, booking_end=booking_end)


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
