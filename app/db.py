"""SQLite helpers: init schema and seed the demo admin user (hash only)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import Flask, current_app, g

from app.auth_utils import check_password, hash_password

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin"


def get_db_path(app: Flask | None = None) -> Path:
    cfg_app = app or current_app
    return Path(cfg_app.config["DATABASE"])


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        path = get_db_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def close_db(_e=None) -> None:
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db(app: Flask | None = None) -> None:
    """Create tables if needed and seed admin with a bcrypt hash."""
    cfg_app = app or current_app
    with cfg_app.app_context():
        db = get_db()
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
            """
        )
        db.commit()
        seed_admin_user(db)


def seed_admin_user(db: sqlite3.Connection | None = None) -> None:
    """Insert admin once; password stored as bcrypt hash only."""
    conn = db or get_db()
    row = conn.execute(
        "SELECT id FROM users WHERE username = ?",
        (DEFAULT_ADMIN_USERNAME,),
    ).fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (DEFAULT_ADMIN_USERNAME, hash_password(DEFAULT_ADMIN_PASSWORD)),
        )
        conn.commit()


def get_user_by_username(username: str) -> sqlite3.Row | None:
    return get_db().execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()


def verify_user_password(username: str, password: str) -> sqlite3.Row | None:
    """Return user row if credentials match; never log the password."""
    user = get_user_by_username(username)
    if user is None:
        return None
    if not check_password(password, user["password_hash"]):
        return None
    return user


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
    init_db(app)
