"""Session auth helpers."""

from __future__ import annotations

from functools import wraps

from flask import redirect, request, session, url_for


def login_user(user_id: int, username: str) -> None:
    session.clear()
    session["user_id"] = user_id
    session["username"] = username
    session.permanent = False


def logout_user() -> None:
    session.clear()


def current_username() -> str | None:
    return session.get("username")


def is_authenticated() -> bool:
    return session.get("user_id") is not None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for("main.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped
