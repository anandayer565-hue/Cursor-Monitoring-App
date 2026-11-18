"""Server registry tests (Phase 3)."""


def _login(client):
    client.post("/login", data={"username": "admin", "password": "admin"})


def test_add_server_success(client_no_csrf):
    _login(client_no_csrf)
    res = client_no_csrf.post(
        "/servers/new",
        data={
            "display_name": "Local box",
            "hostname": "127.0.0.1",
            "ssh_port": 22,
            "ssh_username": "jumpuser9",
            "ssh_password": "secret",
            "ssh_key_path": "",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Local box" in res.data
    assert b"secret" not in res.data  # password never shown on list


def test_reject_non_localhost(client_no_csrf):
    _login(client_no_csrf)
    res = client_no_csrf.post(
        "/servers/new",
        data={
            "display_name": "Remote",
            "hostname": "8.8.8.8",
            "ssh_port": 22,
            "ssh_username": "root",
            "ssh_password": "x",
        },
        follow_redirects=True,
    )
    assert b"localhost" in res.data.lower() or b"127.0.0.1" in res.data
    assert b"Remote" not in res.data or b"Add server" in res.data


def test_require_password_or_key(client_no_csrf):
    _login(client_no_csrf)
    res = client_no_csrf.post(
        "/servers/new",
        data={
            "display_name": "No auth",
            "hostname": "localhost",
            "ssh_port": 22,
            "ssh_username": "u",
            "ssh_password": "",
            "ssh_key_path": "",
        },
        follow_redirects=True,
    )
    assert b"password or a key path" in res.data


def test_missing_display_name(client_no_csrf):
    _login(client_no_csrf)
    res = client_no_csrf.post(
        "/servers/new",
        data={
            "display_name": "",
            "hostname": "127.0.0.1",
            "ssh_port": 22,
            "ssh_username": "u",
            "ssh_password": "p",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Add server" in res.data
