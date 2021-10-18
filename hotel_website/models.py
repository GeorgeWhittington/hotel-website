from typing import Optional

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


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


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


class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    peak_price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    off_peak_price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)

    location_id = db.Column(db.Integer, db.ForeignKey("location.id"))
    location = db.relationship("Location", backref=db.backref("hotels", lazy=True))
    currency_id = db.Column(db.Integer, db.ForeignKey("currency.id"))
    currency = db.relationship("Currency", backref=db.backref("hotels", lazy=True))


class Roomtype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_type = db.Column(db.String(1), unique=True, nullable=False)
    max_occupants = db.Column(db.Integer, nullable=False)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    hotel_id = db.Column(db.Integer, db.ForeignKey("hotel.id"))
    hotel = db.relationship("Hotel", backref=db.backref("rooms", lazy=True))
    room_type_id = db.Column(db.Integer, db.ForeignKey("roomtype.id"))
    room_type = db.relationship("Roomtype", backref=db.backref("rooms", lazy=True))


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