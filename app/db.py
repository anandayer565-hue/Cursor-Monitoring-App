"""SQLite helpers: schema, seed admin, servers, metric samples."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from flask import Flask, current_app, g

from app.auth_utils import check_password, hash_password

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin"
HISTORY_RETENTION_MINUTES = 60


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
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                display_name TEXT NOT NULL,
                hostname TEXT NOT NULL,
                ssh_port INTEGER NOT NULL DEFAULT 22,
                ssh_username TEXT NOT NULL,
                ssh_password TEXT,
                ssh_key_path TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS metric_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                collected_at TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
            );
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


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def list_servers() -> list[sqlite3.Row]:
    return get_db().execute(
        """
        SELECT id, display_name, hostname, ssh_port, ssh_username,
               ssh_password, ssh_key_path, created_at
        FROM servers
        ORDER BY display_name COLLATE NOCASE
        """
    ).fetchall()


def get_server(server_id: int) -> sqlite3.Row | None:
    return get_db().execute(
        """
        SELECT id, display_name, hostname, ssh_port, ssh_username,
               ssh_password, ssh_key_path, created_at
        FROM servers WHERE id = ?
        """,
        (server_id,),
    ).fetchone()


def create_server(
    *,
    display_name: str,
    hostname: str,
    ssh_port: int,
    ssh_username: str,
    ssh_password: str | None,
    ssh_key_path: str | None,
) -> int:
    db = get_db()
    cur = db.execute(
        """
        INSERT INTO servers (
            display_name, hostname, ssh_port, ssh_username,
            ssh_password, ssh_key_path, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            display_name,
            hostname,
            ssh_port,
            ssh_username,
            ssh_password,
            ssh_key_path,
            _utc_now_iso(),
        ),
    )
    db.commit()
    return int(cur.lastrowid)


def save_metric_sample(server_id: int, payload: dict[str, Any]) -> int:
    db = get_db()
    cur = db.execute(
        """
        INSERT INTO metric_samples (server_id, collected_at, payload_json)
        VALUES (?, ?, ?)
        """,
        (server_id, _utc_now_iso(), json.dumps(payload)),
    )
    db.commit()
    prune_metric_samples(
        server_id,
        retention_minutes=current_app.config.get(
            "HISTORY_RETENTION_MINUTES", HISTORY_RETENTION_MINUTES
        ),
    )
    return int(cur.lastrowid)


def prune_metric_samples(
    server_id: int | None = None,
    retention_minutes: int = HISTORY_RETENTION_MINUTES,
) -> int:
    """Delete samples older than retention window. Returns rows deleted."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=retention_minutes)
    cutoff_iso = cutoff.replace(microsecond=0).isoformat()
    db = get_db()
    if server_id is None:
        cur = db.execute(
            "DELETE FROM metric_samples WHERE collected_at < ?",
            (cutoff_iso,),
        )
    else:
        cur = db.execute(
            "DELETE FROM metric_samples WHERE server_id = ? AND collected_at < ?",
            (server_id, cutoff_iso),
        )
    db.commit()
    return cur.rowcount


def get_latest_sample(server_id: int) -> dict[str, Any] | None:
    row = get_db().execute(
        """
        SELECT collected_at, payload_json
        FROM metric_samples
        WHERE server_id = ?
        ORDER BY collected_at DESC, id DESC
        LIMIT 1
        """,
        (server_id,),
    ).fetchone()
    if row is None:
        return None
    payload = json.loads(row["payload_json"])
    payload["_collected_at"] = row["collected_at"]
    return payload


def get_history_samples(
    server_id: int,
    retention_minutes: int | None = None,
) -> list[dict[str, Any]]:
    minutes = retention_minutes or current_app.config.get(
        "HISTORY_RETENTION_MINUTES", HISTORY_RETENTION_MINUTES
    )
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    cutoff_iso = cutoff.replace(microsecond=0).isoformat()
    rows = get_db().execute(
        """
        SELECT collected_at, payload_json
        FROM metric_samples
        WHERE server_id = ? AND collected_at >= ?
        ORDER BY collected_at ASC, id ASC
        """,
        (server_id, cutoff_iso),
    ).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        payload = json.loads(row["payload_json"])
        payload["_collected_at"] = row["collected_at"]
        out.append(payload)
    return out


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
    init_db(app)
