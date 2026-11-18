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


def test_server_detail_after_add(client_no_csrf):
    _login(client_no_csrf)
    client_no_csrf.post(
        "/servers/new",
        data={
            "display_name": "Stub host",
            "hostname": "127.0.0.1",
            "ssh_port": 22,
            "ssh_username": "u",
            "ssh_password": "p",
        },
    )
    res = client_no_csrf.get("/servers/1")
    assert res.status_code == 200
    assert b"Read-only metrics" in res.data
    assert b"Listening ports" in res.data or b"No samples yet" in res.data
