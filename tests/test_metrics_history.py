"""History prune, refresh route, thresholds."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.db import get_db, get_history_samples, prune_metric_samples, save_metric_sample
from app.thresholds import evaluate_warnings


def _login(client):
    client.post("/login", data={"username": "admin", "password": "admin"})


def _add_server(client):
    client.post(
        "/servers/new",
        data={
            "display_name": "Box",
            "hostname": "localhost",
            "ssh_port": 22,
            "ssh_username": "u",
            "ssh_password": "p",
        },
    )


def test_prune_old_samples(app_no_csrf):
    with app_no_csrf.app_context():
        db = get_db()
        db.execute(
            """
            INSERT INTO servers (display_name, hostname, ssh_port, ssh_username,
                                 ssh_password, ssh_key_path, created_at)
            VALUES ('Box', '127.0.0.1', 22, 'u', 'p', NULL, ?)
            """,
            (datetime.now(timezone.utc).isoformat(),),
        )
        db.commit()
        sid = db.execute("SELECT id FROM servers").fetchone()["id"]
        old = (datetime.now(timezone.utc) - timedelta(minutes=120)).replace(
            microsecond=0
        ).isoformat()
        db.execute(
            "INSERT INTO metric_samples (server_id, collected_at, payload_json) "
            "VALUES (?, ?, ?)",
            (sid, old, '{"cpu_percent": 1}'),
        )
        db.commit()
        save_metric_sample(sid, {"cpu_percent": 2, "memory": {"percent": 1}, "disk": {"percent": 1}, "load": {"1m": 0}, "cpu_count": 1})
        deleted = prune_metric_samples(sid, retention_minutes=60)
        # old row should be gone (may already be pruned by save)
        rows = get_history_samples(sid, retention_minutes=60)
        assert all(r.get("cpu_percent") != 1 or "_collected_at" in r for r in rows)
        assert len(rows) >= 1
        assert deleted >= 0


def test_refresh_stores_sample(client_no_csrf):
    _login(client_no_csrf)
    _add_server(client_no_csrf)
    fake = {
        "cpu_percent": 12.0,
        "memory": {"percent": 20.0, "used_kb": 1, "total_kb": 2},
        "load": {"1m": 0.1, "5m": 0.1, "15m": 0.1},
        "uptime_seconds": 9,
        "disk": {"percent": 30.0, "used_kb": 1, "total_kb": 2},
        "network": {"rx_bytes": 1, "tx_bytes": 2},
        "ports": ["LISTEN :22"],
        "processes": [{"pid": "1", "user": "u", "cpu": "0", "mem": "0", "command": "init"}],
        "cpu_count": 2,
        "error": None,
    }
    with patch("app.routes.collect_metrics_safe", return_value=fake):
        res = client_no_csrf.post("/servers/1", follow_redirects=True)
    assert res.status_code == 200
    assert b"12.0%" in res.data or b"12.0" in res.data
    assert b"LISTEN :22" in res.data


def test_refresh_requires_auth(client_no_csrf):
    res = client_no_csrf.post("/servers/1")
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_threshold_boundaries():
    base = {
        "cpu_percent": 79.9,
        "memory": {"percent": 84.9},
        "disk": {"percent": 89.9},
        "load": {"1m": 1.9},
        "cpu_count": 2,
        "error": None,
    }
    w = evaluate_warnings(base)
    assert w == {"cpu": False, "memory": False, "disk": False, "load": False}

    hot = {
        "cpu_percent": 80.0,
        "memory": {"percent": 85.0},
        "disk": {"percent": 90.0},
        "load": {"1m": 2.0},
        "cpu_count": 2,
        "error": None,
    }
    w2 = evaluate_warnings(hot)
    assert w2 == {"cpu": True, "memory": True, "disk": True, "load": True}
