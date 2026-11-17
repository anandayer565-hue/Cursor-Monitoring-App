"""Smoke tests for UI routes (authenticated)."""


def _login(client):
    return client.post(
        "/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=True,
    )


def test_home_ok(client_no_csrf):
    _login(client_no_csrf)
    res = client_no_csrf.get("/")
    assert res.status_code == 200
    assert b"Demo Monitor" in res.data


def test_servers_empty(client_no_csrf):
    _login(client_no_csrf)
    res = client_no_csrf.get("/servers")
    assert res.status_code == 200
    assert b"No servers yet" in res.data
    assert b"Add server" in res.data


def test_server_detail_stub(client_no_csrf):
    _login(client_no_csrf)
    res = client_no_csrf.get("/servers/stub")
    assert res.status_code == 200
    assert b"Read-only metrics" in res.data
    assert b"Listening ports" in res.data
