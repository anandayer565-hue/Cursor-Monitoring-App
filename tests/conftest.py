"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    db_path = tmp_path / "test_monitor.db"
    application = create_app(
        {
            "TESTING": True,
            "DATABASE": str(db_path),
            "SECRET_KEY": "test-secret-key",
            "WTF_CSRF_ENABLED": True,
        }
    )
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def app_no_csrf(tmp_path):
    """Client-friendly app with CSRF off for focused auth flow tests."""
    db_path = tmp_path / "test_monitor_nocsrf.db"
    application = create_app(
        {
            "TESTING": True,
            "DATABASE": str(db_path),
            "SECRET_KEY": "test-secret-key",
            "WTF_CSRF_ENABLED": False,
        }
    )
    yield application


@pytest.fixture
def client_no_csrf(app_no_csrf):
    return app_no_csrf.test_client()
