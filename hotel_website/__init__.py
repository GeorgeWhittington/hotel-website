import os
import json

from flask import Flask


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    with open(os.path.join(app.instance_path, "config.json")) as f:
        data = json.load(f)
        db_host = data["db_host"]
        db_user = data["db_user"]
        db_password = data["db_password"]
    
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE_HOST=db_host,
        DATABASE_USER=db_user,
        DATABASE_PASSWORD=db_password
    )

    # import and reg blueprints here

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app