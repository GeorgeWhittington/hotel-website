import os
import json

from flask import Flask


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with open(os.path.join(app.instance_path, "config.json")) as f:
        data = json.load(f)
        db_uri = data["db_uri"]
        secret_key = data["secret_key"]
    
    app.config.from_mapping(
        SECRET_KEY=secret_key,  # This should be a cryptographically secure generated value for prod
        SQLALCHEMY_DATABASE_URI=db_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    from .models import db, User, Location, Currency, Hotel, Roomtype, Room, Booking
    db.init_app(app)

    from . import hotels, auth
    app.register_blueprint(auth.bp)
    app.register_blueprint(hotels.bp)

    auth.login_manager.init_app(app)

    return app
