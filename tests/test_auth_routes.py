"""Login / logout / protection tests (Steps 1.3–1.4)."""

import re


def _csrf_token(html: bytes) -> str:
    match = re.search(
        rb'name="csrf_token"[^>]*value="([^"]+)"|'
        rb'value="([^"]+)"[^>]*name="csrf_token"',
        html,
    )
    assert match, "csrf_token input missing"
    return (match.group(1) or match.group(2)).decode()


def test_protected_home_redirects(client):
    res = client.get("/")
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_protected_servers_redirects(client):
    res = client.get("/servers")
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_login_bad_password(client_no_csrf):
    res = client_no_csrf.post(
        "/login",
        data={"username": "admin", "password": "wrong"},
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Invalid credentials" in res.data
    assert client_no_csrf.get("/").status_code == 302


def test_login_success_sets_session(client_no_csrf):
    res = client_no_csrf.post(
        "/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=False,
    )
    assert res.status_code == 302
    assert res.headers["Location"].endswith("/")
    home = client_no_csrf.get("/")
    assert home.status_code == 200
    assert b"Demo Monitor" in home.data


def test_logout_clears_session(client_no_csrf):
    client_no_csrf.post("/login", data={"username": "admin", "password": "admin"})
    res = client_no_csrf.post("/logout", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]
    assert client_no_csrf.get("/").status_code == 302


def test_login_rejects_missing_csrf(client):
    res = client.post(
        "/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=False,
    )
    assert res.status_code == 400


def test_login_succeeds_with_csrf(client):
    page = client.get("/login")
    token = _csrf_token(page.data)
    res = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "admin",
            "csrf_token": token,
        },
        follow_redirects=False,
    )
    assert res.status_code == 302
    assert client.get("/").status_code == 200
