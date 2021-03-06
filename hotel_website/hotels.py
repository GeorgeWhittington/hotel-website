# George Whittington, Student ID: 20026036, 2022

from datetime import date, timedelta
import calendar

from sqlalchemy import or_, and_, not_, func, text
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_weasyprint import HTML, render_pdf
from wtforms.validators import Length

from .models import db, Location, Booking, Room, Roomtype, Currency
from .forms import WhereToForm, BookingForm
from .constants import CURRENCY_SYMBOLS, ROOM_TYPES, LOCATION_ERR, DURATION_ERR, GUESTS_ERR

bp = Blueprint("hotels", __name__)


@bp.route("/", methods=["GET", "POST"])
def home():
    form = WhereToForm()
    locations = Location.query.order_by(Location.name).all()
    form.location.choices = [(l.id, l.name) for l in locations]

    if request.method == "POST":
        form_data = form.check()
        if form_data:
            return redirect(url_for("hotels.search", **form_data))

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


@bp.route("/search", methods=["GET", "POST"])
def search():
    form = WhereToForm()
    locations = Location.query.order_by(Location.name).all()
    location_ids = [loc.id for loc in locations]
    form.location.choices = [(loc.id, loc.name) for loc in locations]

    if request.method == "POST":
        form_data = form.check()
        if form_data:
            return redirect(url_for("hotels.search", **form_data))

        return render_template("hotels/search.html", form=form, room_types=ROOM_TYPES)
    else:
        location = request.args.get("location", type=int)
        booking_start = request.args.get("booking_start", type=date.fromisoformat)
        booking_end = request.args.get("booking_end", type=date.fromisoformat)
        guests = request.args.get("guests", type=int)

        # If url args are valid, prefill form with them.
        if location in location_ids:
            form.location.data = location
        else:
            location = None
            flash(LOCATION_ERR)

        if not WhereToForm.test_duration(booking_start, booking_end):
            form.booking_start.data = booking_start
            form.booking_end.data = booking_end
        else:
            booking_start = None
            booking_end = None
            flash(DURATION_ERR)

        if not WhereToForm.test_guests(guests):
            form.guests.data = guests
        else:
            guests = None
            flash(GUESTS_ERR)

    # Invalid search, don't populate results
    if any(item is None for item in [location, booking_start, booking_end, guests]):
        return render_template("hotels/search.html", form=form, room_types=ROOM_TYPES)

    # Find all rooms matching filters
    # Logic for testing if there is any overlap of ranges comes from:
    # https://stackoverflow.com/a/3269471
    results = Room.query.with_entities(Location, Roomtype)
    results = results.join(Room.location).join(Room.room_type).join(Room.bookings, isouter=True)
    results = results.where(
        Roomtype.max_occupants >= guests,
        or_(
            Booking.id == None,  # noqa: E711
            not_(and_(
                booking_start <= Booking.booking_end,
                Booking.booking_start <= booking_end
            ))  # NOT (x1 <= y2 AND y1 <= x2)
        )
    ).group_by(Roomtype.id, Location.id)

    if location:
        results = results.where(Location.id == location)

    results = results.all()

    currency_acronym = request.cookies.get("current_currency", default="GBP")
    currency = Currency.query.filter_by(acronym=currency_acronym).first()

    rooms = []
    for location, room_type in results:
        symbol = CURRENCY_SYMBOLS[currency_acronym]

        price, discount_price = location.find_room_prices(
            room_type=room_type, booking_start=booking_start,
            booking_end=booking_end, currency=currency, guests=guests)

        rooms.append((location, room_type, guests, price, discount_price, symbol))

    # Get duration string, cut off HH:MM:SS data at the end
    booking_duration = str(booking_end - booking_start + timedelta(days=1))[:-9]

    return render_template(
        "hotels/search.html", form=form, results=rooms, room_types=ROOM_TYPES,
        booking_start=booking_start, booking_end=booking_end, booking_duration=booking_duration)


@bp.route("/room", methods=["GET", "POST"])
@login_required
def room():
    location_ids = [loc_id for loc_id, in Location.query.with_entities(Location.id).all()]
    room_type_ids = [rtype_id for rtype_id, in Roomtype.query.with_entities(Roomtype.id).all()]

    location = request.args.get("location", type=int)
    room_type = request.args.get("room_type", type=int)
    booking_start = request.args.get("booking_start", type=date.fromisoformat)
    booking_end = request.args.get("booking_end", type=date.fromisoformat)
    guests = request.args.get("guests", type=int)

    if location not in location_ids:
        location = None
        flash(LOCATION_ERR)

    if room_type not in room_type_ids:
        room_type = None
        flash("Invalid room type selected.")

    if WhereToForm.test_duration(booking_start, booking_end):
        booking_start = None
        booking_end = None
        flash(DURATION_ERR)

    if WhereToForm.test_guests(guests):
        guests = None
        flash(GUESTS_ERR)

    if None in (location, room_type, booking_start, booking_end, guests):
        return redirect(url_for("hotels.home"))

    location_obj = Location.query.get(location)
    room_type_obj = Roomtype.query.get(room_type)

    if room_type_obj.max_occupants < guests:
        flash("Too many guests for the room type selected.")
        return redirect(url_for("hotels.home"))

    rooms = Room.query.outerjoin(Room.bookings).where(
        Room.room_type_id == room_type,
        Room.location_id == location,
        or_(
            Booking.id == None,  # noqa: E711
            not_(and_(
                booking_start <= Booking.booking_end,
                Booking.booking_start <= booking_end)))
    ).group_by(Room).all()

    if len(rooms) == 0:
        flash("No {room_type} rooms at {location} in the period {start} - {end}".format(
            room_type=ROOM_TYPES[room_type_obj.room_type],
            location=location_obj.name,
            start=booking_start.isoformat(),
            end=booking_end.isoformat()
        ))
        return redirect(url_for("hotels.home"))

    currency_acronym = request.cookies.get("current_currency", default="GBP")
    currency = Currency.query.filter_by(acronym=currency_acronym).first()

    symbol = CURRENCY_SYMBOLS[currency_acronym]

    price, discount_price = location_obj.find_room_prices(
        room_type=room_type_obj, booking_start=booking_start,
        booking_end=booking_end, currency=currency, guests=guests)

    form = BookingForm()

    if request.method == "POST":
        if form.validate_on_submit():
            booking = Booking(
                guests=guests,
                booking_start=booking_start,
                booking_end=booking_end,
                name=form.full_name.data,
                email=form.email.data,
                address_1=form.address.address_1.data,
                address_2=form.address.address_2.data,
                postcode=form.address.postcode.data,
                country=form.address.country.data,
                card_type=form.card_details.card_type.data,
                card_number=form.card_details.card_number.data,
                expiry_date=date(
                    year=form.card_details.expiry_date.expiry_year.data,
                    month=form.card_details.expiry_date.expiry_month.data,
                    day=1),
                currency=currency,
                room=rooms[0],  # Select first of available rooms
                user=current_user)
            db.session.add(booking)
            db.session.commit()

            return redirect(url_for("hotels.room_confirm", booking_id=booking.id))

        if form.card_details.card_number.errors:
            flash("Please enter a valid card number, only numbers and spaces are allowed.")

        if form.card_details.security_code.errors:
            flash("Please enter a valid 3 or 4 digit security code.")

    return render_template(
        "hotels/room.html", rooms=rooms, room_types=ROOM_TYPES,
        location=location_obj, room_type=room_type_obj, form=form,
        booking_start=booking_start, booking_end=booking_end,
        symbol=symbol, price=price, discount_price=discount_price,
        guests=guests, length_validator=Length, isinstance=isinstance)


@bp.route("/room_confirm/<booking_id>")
@login_required
def room_confirm(booking_id):
    booking = Booking.query.get(booking_id)

    if not booking:
        flash("Invalid booking.")
        return redirect(url_for("hotels.home"))

    if booking.booking_end < date.today():
        flash("That booking is in the past.")
        return redirect(url_for("hotels.home"))

    return render_template("/hotels/room_confirm.html", booking_id=booking_id)


@bp.route("/booking_<booking_id>.pdf")
@login_required
def booking_pdf(booking_id):
    booking = Booking.query.get(booking_id)

    if not booking:
        flash("Invalid booking.")
        return redirect(url_for("hotels.home"))

    if booking.booking_end < date.today():
        flash("That booking is in the past.")
        return redirect(url_for("hotels.home"))

    if not (current_user.admin or booking.user.id == current_user.id):
        flash("You are not authorised to view this booking.")
        return redirect(url_for("hotels.home"))

    symbol = CURRENCY_SYMBOLS[booking.currency.acronym]
    price, discount_price = booking.find_room_prices()

    html = render_template(
        "/pdf/booking.html", booking=booking, ROOM_TYPES=ROOM_TYPES,
        price=price, discount_price=discount_price, symbol=symbol)
    return render_pdf(HTML(string=html))


@bp.route("/delete_booking/<booking_id>", methods=["GET", "POST"])
@login_required
def delete_booking(booking_id):
    booking = Booking.query.get(booking_id)

    if not booking:
        flash("Invalid booking.")
        return redirect(url_for("hotels.home"))

    if booking.booking_end < date.today():
        flash("That booking is in the past.")
        return redirect(url_for("hotels.home"))

    if booking.user.id != current_user.id:
        flash("You are not authorised to cancel this booking.")
        return redirect(url_for("hotels.home"))

    symbol = CURRENCY_SYMBOLS[booking.currency.acronym]
    price, discount_price = booking.find_room_prices()

    cancel_price = discount_price if discount_price else price
    diff = (booking.booking_start - date.today()).days

    if diff < 30:
        pass
    elif diff < 60:
        cancel_price * 0.5
    else:
        cancel_price = 0

    if request.method == "POST":
        db.session.delete(booking)
        db.session.commit()
        flash("Booking cancelled.")
        return redirect(url_for("hotels.home"))

    return render_template(
        "/hotels/delete_booking.html", booking_id=booking_id, symbol=symbol,
        cancel_price=cancel_price)


@bp.route("/privacy_policy")
def privacy_policy():
    return render_template("privacy.html")
