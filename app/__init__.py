"""Flask application factory for the local demo monitor."""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask
from flask_wtf import CSRFProtect

csrf = CSRFProtect()


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        instance_relative_config=True,
    )

    # Prefer env; fallback is for local demo only (not production-safe).
    default_db = Path(app.instance_path) / "monitor.db"
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me-local-demo"),
        DATABASE=str(default_db),
        WTF_CSRF_ENABLED=True,
    )

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    # Ensure DB parent exists when DATABASE is overridden (e.g. tests).
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)

    csrf.init_app(app)

    from app import db as db_module
    from app.routes import bp as main_bp

    db_module.init_app(app)
    app.register_blueprint(main_bp)

    return app
