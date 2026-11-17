"""SQLite bootstrap / seed tests (Step 1.2)."""

from app.auth_utils import check_password
from app.db import DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME, get_db


def test_admin_seeded_with_verifiable_hash(app):
    with app.app_context():
        row = get_db().execute(
            "SELECT username, password_hash FROM users WHERE username = ?",
            (DEFAULT_ADMIN_USERNAME,),
        ).fetchone()
        assert row is not None
        assert row["username"] == "admin"
        assert row["password_hash"].startswith("$2")
        assert check_password(DEFAULT_ADMIN_PASSWORD, row["password_hash"]) is True
        assert "admin" not in row["password_hash"]  # plaintext not stored as-is


def test_seed_is_idempotent(app):
    with app.app_context():
        from app.db import seed_admin_user

        seed_admin_user()
        seed_admin_user()
        count = get_db().execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        assert count == 1
