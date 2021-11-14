from datetime import date

from sqlalchemy import or_, and_, not_
from flask import Blueprint, render_template, request, flash, redirect, url_for

from .models import Location, Hotel, Booking, Room, Roomtype
from .forms import WhereToForm

bp = Blueprint("hotels", __name__)


@bp.route("/")
def home():
    form = WhereToForm()
    locations = Location.query.order_by(Location.name).all()
    form.location.choices = [(l.id, l.name) for l in locations]

    return render_template("hotels/home.html", form=form, locations=locations)


@bp.route("/search")
def search():
    form = WhereToForm()
    locations = Location.query.order_by(Location.name).all()
    form.location.choices = [(l.id, l.name) for l in locations]

    location = request.args.get("location", type=int)
    booking_start = request.args.get("booking_start", type=date.fromisoformat)
    booking_end = request.args.get("booking_end", type=date.fromisoformat)
    guests = request.args.get("guests", 1, type=int)

    if location not in [l.id for l in locations]:
        location = None
    else:
        form.location.data = location

    if (booking_start is None or
            booking_end is None or
            booking_start < date.today() or
            booking_end <= date.today() or
            booking_start > booking_end):
        booking_start = form.booking_start.data
        booking_end = form.booking_end.data
    else:
        form.booking_start.data = booking_start
        form.booking_end.data = booking_end

    if guests < 1:
        guests = 1
    else:
        form.guests.data = guests

    # Logic for testing if there is any overlap of ranges comes from: https://stackoverflow.com/a/3269471
    results = Room.query.with_entities(Hotel.location_id, Room.room_type_id)
    results = results.join(Room.hotel).join(Room.room_type).join(Room.bookings, isouter=True)
    results = results.where(
        Roomtype.max_occupants >= guests,
        or_(
            Booking.id == None,
            not_(and_(
                booking_start <= Booking.booking_end,
                Booking.booking_start <= booking_end    
            )) # !(x1 <= y2 AND y1 <= x2)
        )
    ).group_by(Roomtype.id, Hotel.id)

    if location:
        results = results.where(Hotel.location.has(id=location))

    results = results.all()

    locations = {l.id: l for l in locations}
    room_types = {rt.id: rt for rt in Roomtype.query.all()}

    results = [(locations[l_id], room_types[rt_id])  for l_id, rt_id in results]

    return render_template("hotels/search.html",
        form=form, results=results,
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
    
    if form.location.errors:
        flash("Please select a location from the list provided.")
    
    referrer = request.referrer[8:]  # Cut off http/https prefix
    referrer_path = referrer[referrer.find("/"):]  # Slice by first / for the path

    lookup = {
        "/": "hotels.home",
        "/search": "hotels.search"
    }

    return redirect(url_for(lookup.get(referrer_path, "hotels.home")))