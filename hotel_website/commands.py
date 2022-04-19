# George Whittington, Student ID: 20026036, 2022

import click
from flask import Blueprint

from .models import db, User, Location, Currency, Roomtype, Room, Booking  # noqa: F401

bp = Blueprint("commands", __name__)


def create_db_manually():
    """Creates the tables defined in hotel_website/models.py. Only run this once, when the database is empty."""
    db.create_all()


def fill_db_manually():
    """Populates the database with data, run after the tables are created."""
    currencies = [
        ("British Pound Sterling", "GBP", 1.0),
        ("Euro", "EUR", 1.2),
        ("United States Dollar", "USD", 1.6)
    ]

    for full_name, acronym, conversion_rate in currencies:
        db.session.add(Currency(full_name=full_name, acronym=acronym, conversion_rate=conversion_rate))

    db.session.commit()

    pounds = Currency.query.filter_by(acronym="GBP").first()

    locations = [
        ("Aberdeen", pounds, 140.0, 60.0, "images/aberdeen.jpg", "A picture of a street in Aberdeen."),
        ("Belfast", pounds, 130.0, 60.0, "images/belfast.jpg", "A picture of a street in Belfast."),
        ("Birmingham", pounds, 150.0, 70.0, "images/birmingham.jpg", "A picture of the skyline in Birmingham."),
        ("Bristol", pounds, 140.0, 70.0, "images/bristol.jpg", "A picture taken in Bristol of the suspension bridge and the buildings near it."),
        ("Cardiff", pounds, 120.0, 60.0, "images/cardiff.jpg", "A picture taken from Cardiff bay of the city."),
        ("Edinburgh", pounds, 160.0, 70.0, "images/edinburgh.jpg", "A picture of Edinburgh taken from somewhere high."),
        ("Glasgow", pounds, 150.0, 70.0, "images/glasgow.jpg", "A picture of Glasgow taken from somewhere high."),
        ("London", pounds, 200.0, 80.0, "images/london.jpg", "A picture taken in London from above the Thames of the river and buildings on either side."),
        ("Manchester", pounds, 180.0, 80.0, "images/manchester.jpg", "A picture taken in Manchester from the intersection of two streets."),
        ("Newcastle", pounds, 100.0, 60.0, "images/newcastle.jpg", "A picture of the river Tyne in Newcastle."),
        ("Norwich", pounds, 100.0, 60.0, "images/norwich.jpg", "A picture of Norwich, the sun is setting."),
        ("Nottingham", pounds, 120.0, 70.0, "images/nottingham.jpg", "A picture of Nottingham."),
        ("Oxford", pounds, 180.0, 70.0, "images/oxford.jpg", "A picture of Oxford, taken from somewhere high."),
        ("Plymouth", pounds, 180.0, 50.0, "images/plymouth.jpg", "A picture of Plymouth, the sea is in frame."),
        ("Swansea", pounds, 120.0, 50.0, "images/swansea.jpg", "A picture of Swansea.")
    ]

    for name, currency, peak_price, off_peak_price, image, image_alt_text in locations:
        db.session.add(Location(
            name=name, currency=currency, peak_price=peak_price,
            off_peak_price=off_peak_price, image=image,
            image_alt_text=image_alt_text
        ))

    room_types = [
        ("S", 1),
        ("D", 2),
        ("F", 6)
    ]

    for room_type, max_occupants in room_types:
        db.session.add(Roomtype(room_type=room_type, max_occupants=max_occupants))

    db.session.commit()

    db.session.add(User.create_user(
        username="admin",
        raw_password="password",  # in production this should be actually secure
        admin=True))

    # Location name: total rooms there
    hotels = {
        "Aberdeen": 80,
        "Belfast": 80,
        "Birmingham": 90,
        "Bristol": 90,
        "Cardiff": 80,
        "Edinburgh": 90,
        "Glasgow": 100,
        "London": 120,
        "Manchester": 110,
        "Newcastle": 80,
        "Norwich": 80,
        "Nottingham": 100,
        "Oxford": 80,
        "Plymouth": 80,
        "Swansea": 80
    }

    # Room type: proportion of total rooms of a type
    room_types = {
        "S": 0.3,
        "D": 0.5,
        "F": 0.2
    }

    room_type_query = Roomtype.query.all()
    room_type_lookup = {rt.room_type: rt for rt in room_type_query}

    for city, no_rooms in hotels.items():
        calculated_room_types = {
            room_type: int(percent * no_rooms)
            for room_type, percent in room_types.items()}

        location = Location.query.filter_by(name=city).first()

        for room_type in calculated_room_types.keys():
            for _ in range(calculated_room_types[room_type]):
                room = Room(location=location, room_type=room_type_lookup[room_type])
                db.session.add(room)

    db.session.commit()


@bp.cli.command()
def create_db():
    """Creates the tables defined in hotel_website/models.py. Only run this once, when the database is empty."""
    create_db_manually()
    click.echo("All tables created.")


@bp.cli.command()
def fill_db():
    """Populates the database with data, run after the tables are created."""
    fill_db_manually()
    click.echo("Database populated.")
