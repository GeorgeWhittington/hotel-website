from typing import Union, Type, Tuple
from datetime import date, timedelta
import calendar

from sqlalchemy.sql import expression, func
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

from .constants import PEAK_PRICING, SINGLE_ROOM, DOUBLE_ROOM_ONE_GUEST, DOUBLE_ROOM_TWO_GUESTS, FAMILY_ROOM

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(102), nullable=False)
    admin = db.Column(db.Boolean, server_default=expression.false(), nullable=False)

    def __str__(self):
        return self.username

    def update_password(self, raw_password: str) -> None:
        self.password = generate_password_hash(
            raw_password,
            method="pbkdf2:sha256:150000",
            salt_length=16)

    @staticmethod
    def get(user_id: str) -> Union["User", None]:
        user = User.query.get(user_id)

        if user:
            return user

        return None

    @staticmethod
    def create_user(username: str, raw_password: str, admin: bool = False) -> Type["User"]:
        """Returns a new user created with parameters provided, the raw_password is hashed."""
        # Specifying exact hash parameters incase the default changes
        return User(
            username=username,
            password=generate_password_hash(
                raw_password,
                method="pbkdf2:sha256:150000",
                salt_length=16),
            admin=admin
        )


class Currency(db.Model):
    """Table for the currencies that the hotels accept.

    Conversion rate is like so: (GBP * EUR conversion_rate) = amount in EUR
    So, GBP's conversion_rate value *must* be 1.0.

    Acronyms are in ISO 4217 format.
    """
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50), unique=True, nullable=False)
    acronym = db.Column(db.String(3), unique=True, nullable=False)
    conversion_rate = db.Column(db.Numeric(precision=10, scale=2), nullable=False)

    def __str__(self):
        return self.full_name


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image = db.Column(db.String(1024), nullable=True)  # Long, for image paths
    image_alt_text = db.Column(db.Text, nullable=True)
    peak_price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    off_peak_price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)

    currency_id = db.Column(db.Integer, db.ForeignKey("currency.id"))
    currency = db.relationship("Currency", backref=db.backref("hotels", lazy=True))

    def __str__(self):
        return self.name

    def find_room_prices(
            self,
            room_type: Type["Roomtype"],
            booking_start: date,
            booking_end: date,
            currency: Currency,
            guests: int,
            date_booked: date = None) -> Tuple[float, Union[float, None]]:
        """Calculates the normal and discounted price of a room at a location.
        The price returned is in the currency supplied.
        """
        if not date_booked:
            date_booked = date.today()

        # Finding number of days that are part of the duration in each month
        # adapted from: https://stackoverflow.com/a/45816728
        current = booking_start
        months = [current]

        # Find each month that is part of the duration
        current = current.replace(day=1)
        while current <= booking_end:
            current += timedelta(days=32)
            current = current.replace(day=1)
            months.append(date(current.year, current.month, 1))

        # Find days within duration for each month
        durations = []
        for i, month in enumerate(months[:-1]):
            # check on first iteration if the start and end are in the same month,
            # need to calculate N.O. days differently in that case
            if (i == 0 and
                    booking_start.year == booking_end.year and
                    booking_start.month == booking_end.month):
                # Duration inclusive of start day, so + 1
                durations.append((month.month, booking_end.day - booking_start.day + 1))
                continue

            if month.month == booking_end.month and month.year == booking_end.year:
                durations.append((booking_end.month, booking_end.day))
            else:
                month_range = calendar.monthrange(month.year, month.month)[1]
                duration = (month_range - month.day) + 1  # Duration inclusive of start day, so + 1
                durations.append((month.month, duration))

        room_multiplier = SINGLE_ROOM
        if room_type.room_type == "D":
            room_multiplier = DOUBLE_ROOM_ONE_GUEST if guests == 1 else DOUBLE_ROOM_TWO_GUESTS
        if room_type.room_type == "F":
            room_multiplier = FAMILY_ROOM

        total_price = 0.0
        for month, days in durations:
            base_price = self.peak_price if PEAK_PRICING[month] else self.off_peak_price
            total_price += float(base_price) * room_multiplier * days

        if currency != self.currency:
            total_price *= float(currency.conversion_rate)

        days_in_advance = (booking_start - date_booked).days
        if days_in_advance >= 80:
            discount_price = total_price * 0.80
        elif days_in_advance >= 60:
            discount_price = total_price * 0.90
        elif days_in_advance >= 45:
            discount_price = total_price * 0.95
        else:
            discount_price = None

        return total_price, discount_price


class Roomtype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_type = db.Column(db.String(1), unique=True, nullable=False)
    max_occupants = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return self.room_type


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    location_id = db.Column(db.Integer, db.ForeignKey("location.id"))
    location = db.relationship("Location", backref=db.backref("rooms", lazy=True))
    room_type_id = db.Column(db.Integer, db.ForeignKey("roomtype.id"))
    room_type = db.relationship("Roomtype", backref=db.backref("rooms", lazy=True))

    def __str__(self):
        return f"Room(id={self.id}, location={self.location}, room_type={self.room_type})"


class Booking(db.Model):
    """ Table for bookings of rooms.

    Card information is stored here, but *not* cvc, as storing this
    is illegal.
    """
    # TODO: Assess if storing the name/address/card details on this table breaks
    # normalisation
    # TODO: Store currency in use when booking was created
    id = db.Column(db.Integer, primary_key=True)
    guests = db.Column(db.Integer, nullable=False)
    booking_start = db.Column(db.Date, nullable=False)
    booking_end = db.Column(db.Date, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())  # TODO: is this actually necessary?

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)

    address_1 = db.Column(db.String(200), nullable=False)
    address_2 = db.Column(db.String(200), nullable=True)
    postcode = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(2), nullable=False)

    card_type = db.Column(db.String(1), nullable=False)
    card_number = db.Column(db.String(50), nullable=False)
    expiry_date = db.Column(db.Date(), nullable=False)

    room_id = db.Column(db.Integer, db.ForeignKey("room.id"))
    room = db.relationship("Room", backref=db.backref("bookings", lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref=db.backref("bookings", lazy=True))

    def find_room_prices(self, currency):
        return self.room.location.find_room_prices(
            room_type=self.room.room_type,
            booking_start=self.booking_start,
            booking_end=self.booking_end,
            currency=currency,
            guests=self.guests,
            date_booked=date(
                year=self.date_created.year,
                month=self.date_created.month,
                day=self.date_created.day))


def rooms_available(self, start: date, end: date, **kwargs) -> int:
    """Finds the number of rooms available at a location during a time period

    Keyword Arguments:
        room_types: A tuple of Roomtype objects, by default all room types are selected
    """
    room_types = kwargs.get("room_types", [rt for rt in Roomtype.query.all()])
    try:
        _ = list(room_types)[0]
    except TypeError:
        raise ValueError("Invalid room_types value, a list/tuple of room_types must be provided") from TypeError

    if isinstance(room_types[0], Roomtype):
        room_types = [rt.id for rt in room_types]

    rooms = Room.query.with_entities(func.count(Room.id)).where(
        Room.location_id == self.id,
        Room.room_type_id.in_(room_types)
    ).first()[0]

    rooms_used = Room.query.with_entities(func.count(Room.id))
    rooms_used = rooms_used.outerjoin(Room.bookings).where(
        Room.location_id == self.id,
        Room.room_type_id.in_(room_types),
        Booking.id != None,  # noqa: E711
        # Logic for testing if there is any overlap of ranges from:
        # https://stackoverflow.com/a/3269471
        start <= Booking.booking_end,
        Booking.booking_start <= end
    ).first()[0]

    return rooms - rooms_used


Location.rooms_available = rooms_available
