"""HTTP routes: protected UI + login/logout."""

from __future__ import annotations

from urllib.parse import urlparse

from flask import (
    Blueprint,
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
from app.db import verify_user_password
from app.forms import LoginForm, LogoutForm

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


@bp.get("/")
@login_required
def home():
    return render_template("home.html")


@bp.get("/servers")
@login_required
def servers():
    return render_template("servers.html", servers=[])


@bp.get("/servers/<server_id>")
@login_required
def server_detail(server_id: str):
    return render_template(
        "server_detail.html",
        server_id=server_id,
        server_name="Example host (stub)",
    )


@bp.route("/login", methods=["GET", "POST"])
def login():
    if is_authenticated():
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        username = (form.username.data or "").strip()
        password = form.password.data or ""
        # Do not log password or include it in flash messages.
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
