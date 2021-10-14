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
        db_host = data["db_host"]
        db_name = data["db_name"]
        db_user = data["db_user"]
        db_password = data["db_password"]
    
    app.config.from_mapping(
        SECRET_KEY="dev",  # Generate something actually secure and store it in config.json for prod
        DATABASE_HOST=db_host,
        DATABASE_NAME=db_name,
        DATABASE_USER=db_user,
        DATABASE_PASSWORD=db_password
    )

    from . import hotels, auth
    app.register_blueprint(auth.bp)
    app.register_blueprint(hotels.bp)    

    from . import db
    db.init_app(app)

    return app