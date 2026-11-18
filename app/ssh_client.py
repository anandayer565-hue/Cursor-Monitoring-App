"""SSH client wrapper for localhost metric collection (read-only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import paramiko


class SSHError(Exception):
    """Raised when SSH connect or command execution fails."""


@dataclass
class SSHCredentials:
    hostname: str
    port: int
    username: str
    password: str | None = None
    key_path: str | None = None


def connect_ssh(
    creds: SSHCredentials,
    *,
    timeout: float = 8.0,
    client_factory: Callable[[], paramiko.SSHClient] | None = None,
) -> paramiko.SSHClient:
    """
    Open an SSH session. Agent forwarding is disabled.
    Demo only: storing SSH passwords in SQLite is not production-safe.
    """
    if not creds.password and not creds.key_path:
        raise SSHError("SSH password or key path is required")

    factory = client_factory or paramiko.SSHClient
    client = factory()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    connect_kwargs: dict = {
        "hostname": creds.hostname,
        "port": creds.port,
        "username": creds.username,
        "timeout": timeout,
        "allow_agent": False,
        "look_for_keys": False,
    }
    if creds.key_path:
        connect_kwargs["key_filename"] = creds.key_path
    if creds.password:
        connect_kwargs["password"] = creds.password

    try:
        client.connect(**connect_kwargs)
    except Exception as exc:  # noqa: BLE001 — surface as SSHError for UI
        client.close()
        raise SSHError(f"SSH connection failed: {exc}") from exc
    return client


def run_command(client: paramiko.SSHClient, command: str, timeout: float = 10.0) -> str:
    """Run a fixed remote command (never interpolate untrusted input into shell)."""
    try:
        _stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        code = stdout.channel.recv_exit_status()
    except Exception as exc:  # noqa: BLE001
        raise SSHError(f"Command failed: {exc}") from exc
    if code != 0 and not out.strip():
        raise SSHError(err.strip() or f"Command exited {code}")
    return out
