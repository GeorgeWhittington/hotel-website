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


def init_db():
    db = get_db()
    cursor = db.cursor()

    with current_app.open_resource("schema.sql") as f:
        cursor.execute(f.read(), multi=True)


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Create new tables, if they don't already exist"""
    init_db()
    click.echo("Database initialised.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


class User(UserMixin):
    def get(user_id):
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT id FROM users WHERE id == %s", (user_id))
        row = cursor.fetchone()

        if not row:
            return None
        
        return row[0]