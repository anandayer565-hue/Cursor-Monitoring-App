"""Input validation helpers for the local demo."""

from __future__ import annotations

ALLOWED_HOSTS = frozenset(
    {
        "localhost",
        "127.0.0.1",
        "::1",
    }
)


def normalize_hostname(hostname: str) -> str:
    return (hostname or "").strip().lower().rstrip(".")


def is_localhost_host(hostname: str) -> bool:
    """Demo rule: only the machine running the app may be monitored."""
    return normalize_hostname(hostname) in ALLOWED_HOSTS


def validate_ssh_port(port: int | str) -> int:
    try:
        value = int(port)
    except (TypeError, ValueError) as exc:
        raise ValueError("SSH port must be an integer") from exc
    if not 1 <= value <= 65535:
        raise ValueError("SSH port must be between 1 and 65535")
    return value
