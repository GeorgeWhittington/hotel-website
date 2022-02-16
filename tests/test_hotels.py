from datetime import date, timedelta

import pytest  # noqa: F401

from hotel_website.constants import LOCATION_ERR, DURATION_ERR, GUESTS_ERR

today = date.today()
tomorrow = today + timedelta(days=1)
three_months = today + timedelta(days=91)

where_to_validation = (
    (None, None, None, None, [LOCATION_ERR, DURATION_ERR, GUESTS_ERR]),
    (1, today, tomorrow, None, [GUESTS_ERR]),
    (1, today, tomorrow, 0, [GUESTS_ERR]),
    (1, today, tomorrow, 7, [GUESTS_ERR]),
    (1, today, tomorrow, "one", [GUESTS_ERR]),
    (None, today, tomorrow, 1, [LOCATION_ERR]),
    (0, today, tomorrow, 1, [LOCATION_ERR]),
    (500, today, tomorrow, 1, [LOCATION_ERR]),
    ("Aberdeen", today, tomorrow, 1, [LOCATION_ERR]),
    (1, None, None, 1, [DURATION_ERR]),
    (1, today, None, 1, [DURATION_ERR]),
    (1, None, tomorrow, 1, [DURATION_ERR]),
    (1, today, today, 1, [DURATION_ERR]),
    (1, tomorrow, tomorrow, 1, [DURATION_ERR]),
    (1, tomorrow, today, 1, [DURATION_ERR]),
    (1, today, three_months, 1, [DURATION_ERR]),
    (1, "today", "tomorrow", 1, [DURATION_ERR])
)


def test_home_get(client):
    assert client.get("/").status_code == 200


def test_home_post(client):
    response = client.post("/", data={
        "location": 1,
        "booking_start": today.isoformat(),
        "booking_end": tomorrow.isoformat(),
        "guests": 1
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"No hotel rooms could be found, sorry." not in response.data


@pytest.mark.parametrize(
    ("location", "booking_start", "booking_end", "guests", "errors"),
    where_to_validation)
def test_home_post_validation(client, location, booking_start, booking_end, guests, errors):
    booking_start.isoformat() if isinstance(booking_start, date) else booking_start
    booking_end.isoformat() if isinstance(booking_end, date) else booking_end

    response = client.post("/", data={
        "location": location,
        "booking_start": booking_start,
        "booking_end": booking_end,
        "guests": guests
    })

    assert response.status_code == 200
    for error_msg in errors:
        assert bytes(error_msg, "utf-8") in response.data


def test_search_get(client):
    assert client.get("/search", query_string={
        "location": 1,
        "booking_start": today.isoformat(),
        "booking_end": tomorrow.isoformat(),
        "guests": 1
    }).status_code == 200


@pytest.mark.parametrize(
    ("location", "booking_start", "booking_end", "guests", "errors"),
    where_to_validation)
def test_search_get_validation(client, location, booking_start, booking_end, guests, errors):
    booking_start.isoformat() if isinstance(booking_start, date) else booking_start
    booking_end.isoformat() if isinstance(booking_end, date) else booking_end

    response = client.get("/search", query_string={
        "location": location,
        "booking_start": booking_start,
        "booking_end": booking_end,
        "guests": guests
    })

    print(f"{location} {booking_start} {booking_end} {guests}")

    assert response.status_code == 200
    assert b"No hotel rooms could be found, sorry." in response.data
    for error_msg in errors:
        assert bytes(error_msg, "utf-8") in response.data


def test_search_post(client):
    response = client.post("/search", data={
        "location": 1,
        "booking_start": today.isoformat(),
        "booking_end": tomorrow.isoformat(),
        "guests": 1
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"No hotel rooms could be found, sorry." not in response.data


@pytest.mark.parametrize(
    ("location", "booking_start", "booking_end", "guests", "errors"),
    where_to_validation)
def test_search_post_validation(client, location, booking_start, booking_end, guests, errors):
    booking_start.isoformat() if isinstance(booking_start, date) else booking_start
    booking_end.isoformat() if isinstance(booking_end, date) else booking_end

    response = client.post("/search", data={
        "location": location,
        "booking_start": booking_start,
        "booking_end": booking_end,
        "guests": guests
    })

    assert response.status_code == 200
    for error_msg in errors:
        assert bytes(error_msg, "utf-8") in response.data


def test_search_post_multiple(client):
    response = client.get("/search", query_string={
        "location": 1,
        "booking_start": today.isoformat(),
        "booking_end": tomorrow.isoformat(),
        "guests": 1
    })
    assert response.status_code == 200
    assert b"No hotel rooms could be found, sorry." not in response.data

    response = client.post("/search", data={
        "location": 2,
        "booking_start": today.isoformat(),
        "booking_end": tomorrow.isoformat(),
        "guests": 4
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"No hotel rooms could be found, sorry." not in response.data

    response = client.post("/search", data={
        "location": 2,
        "booking_start": today.isoformat(),
        "booking_end": tomorrow.isoformat(),
        "guests": 9
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"No hotel rooms could be found, sorry." in response.data


def test_room_get(client, auth):
    auth.login()
    assert client.get("/room", query_string={
        "location": 1,
        "booking_start": today.isoformat(),
        "booking_end": tomorrow.isoformat(),
        "guests": 1,
        "room_type": 1
    }).status_code == 200
