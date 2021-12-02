import click
from werkzeug.security import generate_password_hash

from hotel_website import create_app
from hotel_website.models import db

app = create_app()


@app.cli.command()
def createdb():
    db.create_all()
    click.echo("All tables created.")


# Fills the database with stuff that can't be populated with hotel_website/data.sql easily.
# Run the sql in there before running this
@app.cli.command()
def filldb():
    from hotel_website.models import User, Roomtype, Room, Location

    # Create admin user
    user = User(
        username="admin",
        password=generate_password_hash(
            "password",  # in production this should be actually secure
            method="pbkdf2:sha256:150000",
            salt_length=16),
        admin=True)

    db.session.add(user)

    # Add all rooms
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

    room_types = {
        "S": 0.3,
        "D": 0.5,
        "F": 0.2
    }

    room_type_query = Roomtype.query.all()
    room_type_lookup = {rt.room_type: rt for rt in room_type_query}

    for city, rooms in hotels.items():
        calculated_room_types = {
            room_type: int(percent * rooms)
            for room_type, percent in room_types.items()}

        location = Location.query.filter_by(name=city).first()

        for room_type in calculated_room_types.keys():
            for _ in range(calculated_room_types[room_type]):
                room = Room(location=location, room_type=room_type_lookup[room_type])
                db.session.add(room)

    db.session.commit()
    click.echo("Populated db with admin user and rooms.")


if __name__ == "__main__":
    app.run(debug=True)
