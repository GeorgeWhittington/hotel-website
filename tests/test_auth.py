# George Whittington, Student ID: 20026036, 2022

import pytest  # noqa: F401

from hotel_website.models import User


def test_login_get(client):
    assert client.get("/login").status_code == 200


def test_login_post(client, auth):
    auth.login()
    with client.session_transaction() as sess:
        assert sess.get("_user_id") is not None


@pytest.mark.parametrize(
    ("username", "password"),
    (("invalid", "password"), ("test", "invalid")))
def test_login_validation(auth, client, username, password):
    response = auth.login(username, password)
    assert b"The username or password you have entered is invalid." in response.data
    with client.session_transaction() as sess:
        assert sess.get("_user_id") is None


def test_logout(auth, client):
    auth.login()
    response = auth.logout()
    assert b"Logged out." in response.data
    with client.session_transaction() as sess:
        assert sess.get("_user_id") is None


def test_register_get(client):
    client.get("/register").status_code == 200


def test_register_post(client, app, auth):
    response = client.post(
        "/register",
        data={"username": "test_username", "password": "password"},
        follow_redirects=True)

    assert b"Registered." in response.data

    with app.app_context():
        assert User.query.filter_by(username="test_username").first() is not None

    auth.login(username="test_username", password="password")
    with client.session_transaction() as sess:
        assert sess.get("_user_id") is not None


@pytest.mark.parametrize(("username", "password", "message"), (
    ("test", "password", b"The username test is taken."),
    ("aaaaabbbbbcccccddddde", "password", b"Your username cannot be longer than 20 characters."),
    ("", "password", None),
    ("test_username", "", None)
))
def test_register_validation(app, client, username, password, message):
    response = client.post("/register", data={"username": username, "password": password})
    if message:
        assert message in response.data

    # first testcase is checking that a duplicate user is not added
    if username != "test":
        with app.app_context():
            assert User.query.filter_by(username=username).first() is None


def test_my_account_get(client, auth):
    auth.login()
    assert client.get("/my-account").status_code == 200
