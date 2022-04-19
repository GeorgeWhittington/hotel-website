# George Whittington, Student ID: 20026036, 2022

import pytest
from werkzeug.test import TestResponse

from hotel_website import create_app
from hotel_website.commands import create_db_manually, fill_db_manually
from hotel_website.models import db, User


@pytest.fixture
def app():
    app = create_app(testing=True)

    with app.app_context():
        create_db_manually()
        fill_db_manually()
        db.session.add(User.create_user(username="test", raw_password="password"))
        db.session.commit()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username: str = "test", password: str = "password") -> TestResponse:
        return self._client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=True)

    def logout(self):
        return self._client.get("/logout", follow_redirects=True)


@pytest.fixture
def auth(client):
    return AuthActions(client)
