import os
import json

import click
from flask import Flask, render_template
from werkzeug.security import generate_password_hash


def create_app(testing=False):
    app = Flask(__name__, instance_relative_config=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with open(os.path.join(app.instance_path, "config.json")) as f:
        data = json.load(f)
        db_uri = data["db_uri"]
        secret_key = data["secret_key"]

    if testing:
        db_uri = "sqlite://"  # In memory sqlite db for tests

    app.config.from_mapping(
        SECRET_KEY=secret_key,  # This should be a cryptographically secure value for production
        SQLALCHEMY_DATABASE_URI=db_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        FLASK_ADMIN_SWATCH="cerulean")

    from .models import db, User, Location, Currency, Roomtype, Room, Booking  # noqa: F401
    db.init_app(app)

    from . import hotels, auth, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(hotels.bp)

    auth.login_manager.init_app(app)
    admin.admin.init_app(app)  # Admin's views get registered here

    # Provide currency data to all templates during rendering
    @app.context_processor
    def utility_processor():
        currencies = Currency.query.all()
        return dict(currencies=currencies)

    @app.errorhandler(401)
    def error_401(error):
        error_msg = "You need to be logged in to reach that page."
        return render_template("error.html", error_no=401, error_msg=error_msg), 401

    @app.errorhandler(404)
    def error_404(error):
        error_msg = "That page could not be found."
        return render_template("error.html", error_no=404, error_msg=error_msg), 404

    @app.cli.command()
    def createdb():
        """Command to create the tables defined in hotel_website/models.py.
        Only run this once, when the database is empty. Probably do migrations manually.
        """
        db.create_all()
        click.echo("All tables created.")

    @app.cli.command()
    def filldb():
        """Command to populate the database with data. Run after the tables
        are created using createdb.
        """
        currencies = [
            ("British Pound Sterling", "GBP", 1.0),
            ("Euro", "EUR", 1.2),
            ("United States Dollar", "USD", 1.6)
        ]

        for full_name, acronym, conversion_rate in currencies:
            db.session.add(Currency(full_name=full_name, acronym=acronym, conversion_rate=conversion_rate))

        db.session.commit()
        click.echo("Populated db with currencies.")

        pounds = Currency.query.filter_by(acronym="GBP").first()

        locations = [
            ("Aberdeen", pounds, 140.0, 60.0, "images/aberdeen.jpg"),
            ("Belfast", pounds, 130.0, 60.0, "images/belfast.jpg"),
            ("Birmingham", pounds, 150.0, 70.0, "images/birmingham.jpg"),
            ("Bristol", pounds, 140.0, 70.0, "images/bristol.jpg"),
            ("Cardiff", pounds, 120.0, 60.0, "images/cardiff.jpg"),
            ("Edinburgh", pounds, 160.0, 70.0, "images/edinburgh.jpg"),
            ("Glasgow", pounds, 150.0, 70.0, "images/glasgow.jpg"),
            ("London", pounds, 200.0, 80.0, "images/london.jpg"),
            ("Manchester", pounds, 180.0, 80.0, "images/manchester.jpg"),
            ("Newcastle", pounds, 100.0, 60.0, "images/newcastle.jpg"),
            ("Norwich", pounds, 100.0, 60.0, "images/norwich.jpg"),
            ("Nottingham", pounds, 120.0, 70.0, "images/nottingham.jpg"),
            ("Oxford", pounds, 180.0, 70.0, "images/oxford.jpg"),
            ("Plymouth", pounds, 180.0, 50.0, "images/plymouth.jpg"),
            ("Swansea", pounds, 120.0, 50.0, "images/swansea.jpg")
        ]

        for name, currency, peak_price, off_peak_price, image in locations:
            db.session.add(Location(
                name=name, currency=currency, peak_price=peak_price,
                off_peak_price=off_peak_price, image=image
            ))

        db.session.commit()
        click.echo("Populated db with locations.")

        room_types = [
            ("S", 1),
            ("D", 2),
            ("F", 6)
        ]

        for room_type, max_occupants in room_types:
            db.session.add(Roomtype(room_type=room_type, max_occupants=max_occupants))

        db.session.commit()
        click.echo("Populated db with room types.")

        db.session.add(User(
            username="admin",
            password=generate_password_hash(
                "password",  # in production this should be actually secure
                method="pbkdf2:sha256:150000",
                salt_length=16),
            admin=True))

        db.session.commit()
        click.echo("Populated db with admin user.")

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
        click.echo("Populated db with rooms.")
        click.echo("Population of database complete.")

    return app
