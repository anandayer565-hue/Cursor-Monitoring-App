"""HTTP routes: auth, server registry, read-only metrics."""

from __future__ import annotations

import json
from urllib.parse import urlparse

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.auth import (
    current_username,
    is_authenticated,
    login_required,
    login_user,
    logout_user,
)
from app.collectors import collect_metrics_safe
from app.db import (
    create_server,
    get_history_samples,
    get_latest_sample,
    get_server,
    list_servers,
    save_metric_sample,
    verify_user_password,
)
from app.forms import LoginForm, LogoutForm, RefreshForm, ServerForm
from app.ssh_client import SSHCredentials
from app.thresholds import any_warning, evaluate_warnings

bp = Blueprint("main", __name__)


def _safe_next_url(candidate: str | None) -> str | None:
    """Allow only relative local paths (open-redirect safe)."""
    if not candidate:
        return None
    parsed = urlparse(candidate)
    if parsed.scheme or parsed.netloc:
        return None
    if not candidate.startswith("/"):
        return None
    return candidate


def _server_creds(server) -> SSHCredentials:
    return SSHCredentials(
        hostname=server["hostname"],
        port=int(server["ssh_port"]),
        username=server["ssh_username"],
        password=server["ssh_password"] or None,
        key_path=server["ssh_key_path"] or None,
    )


def _history_chart_payload(samples: list[dict]) -> str:
    labels = []
    cpu = []
    mem = []
    disk = []
    for s in samples:
        labels.append(s.get("_collected_at", ""))
        cpu.append(s.get("cpu_percent"))
        mem.append((s.get("memory") or {}).get("percent"))
        disk.append((s.get("disk") or {}).get("percent"))
    return json.dumps({"labels": labels, "cpu": cpu, "memory": mem, "disk": disk})


@bp.get("/")
@login_required
def home():
    return render_template("home.html")


@bp.get("/servers")
@login_required
def servers():
    rows = list_servers()
    # Never pass SSH passwords to the list template.
    safe = [
        {
            "id": r["id"],
            "display_name": r["display_name"],
            "hostname": r["hostname"],
            "ssh_port": r["ssh_port"],
            "ssh_username": r["ssh_username"],
            "auth_method": "key" if r["ssh_key_path"] else "password",
            "warning": any_warning(
                evaluate_warnings(get_latest_sample(r["id"]))
            ),
        }
        for r in rows
    ]
    return render_template("servers.html", servers=safe)


@bp.route("/servers/new", methods=["GET", "POST"])
@login_required
def servers_new():
    form = ServerForm()
    if form.validate_on_submit():
        password = (form.ssh_password.data or "").strip() or None
        key_path = (form.ssh_key_path.data or "").strip() or None
        # Do not log credentials.
        create_server(
            display_name=(form.display_name.data or "").strip(),
            hostname=(form.hostname.data or "").strip(),
            ssh_port=int(form.ssh_port.data),
            ssh_username=(form.ssh_username.data or "").strip(),
            ssh_password=password,
            ssh_key_path=key_path,
        )
        flash("Server added.", "ok")
        return redirect(url_for("main.servers"))
    return render_template("server_form.html", form=form)


@bp.route("/servers/<int:server_id>", methods=["GET", "POST"])
@login_required
def server_detail(server_id: int):
    server = get_server(server_id)
    if server is None:
        flash("Server not found.", "error")
        return redirect(url_for("main.servers"))

    refresh_form = RefreshForm()
    if refresh_form.validate_on_submit():
        metrics = collect_metrics_safe(_server_creds(server))
        save_metric_sample(server_id, metrics)
        if metrics.get("error"):
            flash(f"Refresh failed: {metrics['error']}", "error")
        else:
            flash("Metrics refreshed.", "ok")
        return redirect(url_for("main.server_detail", server_id=server_id))

    latest = get_latest_sample(server_id)
    warnings = evaluate_warnings(latest)
    retention = current_app.config["HISTORY_RETENTION_MINUTES"]
    history = get_history_samples(server_id, retention_minutes=retention)
    chart_json = _history_chart_payload(history)

    return render_template(
        "server_detail.html",
        server=server,
        metrics=latest,
        warnings=warnings,
        refresh_form=refresh_form,
        retention_minutes=retention,
        chart_json=chart_json,
    )


@bp.route("/login", methods=["GET", "POST"])
def login():
    if is_authenticated():
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        username = (form.username.data or "").strip()
        password = form.password.data or ""
        user = verify_user_password(username, password)
        if user is None:
            flash("Invalid credentials.", "error")
        else:
            login_user(user["id"], user["username"])
            nxt = _safe_next_url(request.args.get("next"))
            return redirect(nxt or url_for("main.home"))

    return render_template("login.html", form=form)


@bp.post("/logout")
@login_required
def logout():
    form = LogoutForm()
    if form.validate_on_submit():
        logout_user()
        return redirect(url_for("main.login"))
    flash("Could not sign out. Try again.", "error")
    return redirect(url_for("main.home"))


@bp.app_context_processor
def inject_auth():
    return {
        "current_username": current_username(),
        "is_authenticated": is_authenticated(),
        "logout_form": LogoutForm() if is_authenticated() else None,
    }
