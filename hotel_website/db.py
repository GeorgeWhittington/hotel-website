import click
from flask import current_app, g
from flask.cli import with_appcontext
from flask_login import UserMixin
import mysql.connector
from mysql.connector import errorcode


def get_db():
    if "db" not in g:
        try:
            g.db = mysql.connector.connect(
                user=current_app.config["DATABASE_USER"],
                password=current_app.config["DATABASE_PASSWORD"],
                host=current_app.config["DATABASE_HOST"],
                database=current_app.config["DATABASE_NAME"],)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Access denied to mysql database")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("That mysql database does not exist")
            else:
                print(err)
        
        return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def populate_room_data():
    db = get_db()
    cursor = db.cursor()
    
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

    cursor.execute("SELECT id, type FROM room_types")
    room_ids = cursor.fetchall()
    room_ids = {type: id for id, type in room_ids}

    for city, rooms in hotels.items():
        calculated_room_types = {
            room_type: int(percent * rooms)
            for room_type, percent in room_types.items()}
        
        cursor.execute(
            "SELECT hotels.id FROM hotels INNER JOIN locations ON hotels.location_id = locations.id WHERE %s = locations.location_name",
            (city,))
        hotel_id = cursor.fetchone()[0]

        for room_type in calculated_room_types.keys():
            for _ in range(calculated_room_types[room_type]):
                cursor.execute(
                    "INSERT INTO rooms (hotel_id, type_id) VALUE (%s, %s)",
                    (hotel_id, room_ids[room_type]))
    
    db.commit()


@click.command("populate-room-data")
@with_appcontext
def populate_room_data_command():
    """Populate the database with room data"""
    populate_room_data()
    click.echo("Database populated.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(populate_room_data_command)


class User(UserMixin):
    def get(user_id):
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id))
        row = cursor.fetchone()

        if not row:
            return None
        
        return row[0]