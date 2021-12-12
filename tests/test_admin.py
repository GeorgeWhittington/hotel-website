import pytest  # noqa: F401


@pytest.mark.parametrize(("path"), (
    ("/admin/"),
    ("/admin/user/"),
    ("/admin/location/"),
    ("/admin/currency/"),
    ("/admin/roomtype/"),
    ("/admin/room/"),
    ("/admin/booking/")
))
def test_admin_get(client, auth, path):
    auth.login(username="admin", password="password")
    assert client.get(path).status_code == 200


@pytest.mark.parametrize(("path"), (
    ("/admin/"),
    ("/admin/user/"),
    ("/admin/location/"),
    ("/admin/currency/"),
    ("/admin/roomtype/"),
    ("/admin/room/"),
    ("/admin/booking/")
))
def test_admin_unauthorized(client, path):
    assert client.get(path).status_code == 302
