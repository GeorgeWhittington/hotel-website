from typing import Optional
from datetime import date

from sqlalchemy import or_, and_, not_
from sqlalchemy.sql import expression, func
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(102), nullable=False)
    admin = db.Column(db.Boolean, server_default=expression.false(), nullable=False)

    @staticmethod
    def get(user_id: str) -> Optional["User"]:
        user = User.query.get(user_id)

        if user:
            return user

        return None
    
    def __str__(self):
        return self.username


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
    peak_price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    off_peak_price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)

    currency_id = db.Column(db.Integer, db.ForeignKey("currency.id"))
    currency = db.relationship("Currency", backref=db.backref("hotels", lazy=True))

    def __str__(self):
        return self.name


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
    id = db.Column(db.Integer, primary_key=True)
    guests = db.Column(db.Integer, nullable=False)
    booking_start = db.Column(db.Date, nullable=False)
    booking_end = db.Column(db.Date, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    room_id = db.Column(db.Integer, db.ForeignKey("room.id"))
    room = db.relationship("Room", backref=db.backref("bookings", lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref=db.backref("bookings", lazy=True))


def rooms_available(self, start: date, end: date) -> int:
    # Logic for testing if there is any overlap of ranges comes from: https://stackoverflow.com/a/3269471
    rooms = Room.query.join(Room.location).join(Room.bookings, isouter=True).where(
        Location.id == self.id,
        or_(
            Booking.id == None,
            not_(and_(
                start <= Booking.booking_end,
                Booking.booking_start <= end
            )) # !(x1 <= y2 AND y1 <= x2)
        )
    ).count()
    return rooms


Location.rooms_available = rooms_available