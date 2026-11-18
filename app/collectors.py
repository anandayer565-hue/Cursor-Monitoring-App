"""Read-only metric collectors over SSH. Commands are fixed strings only."""

from __future__ import annotations

import re
from typing import Any, Callable

from app.ssh_client import SSHCredentials, SSHError, connect_ssh, run_command

# Fixed remote commands — do not add user-controlled interpolation.
CMD_CPU = (
    "grep 'cpu ' /proc/stat | awk '{u=$2+$4; t=$2+$4+$5; "
    "if (t>0) printf \"%.2f\", 100*u/t; else print 0}'"
)
CMD_MEM = (
    "awk '/MemTotal/ {t=$2} /MemAvailable/ {a=$2} END "
    "{if(t>0) printf \"%.2f %d %d\", 100*(t-a)/t, (t-a), t; else print \"0 0 0\"}' "
    "/proc/meminfo"
)
CMD_LOAD = "cat /proc/loadavg"
CMD_UPTIME = "cut -d. -f1 /proc/uptime"
CMD_DISK = "df -P / | awk 'NR==2 {gsub(/%/,\"\",$5); print $5, $3, $2}'"
CMD_NET = (
    "awk 'NR>2 {rx+=$2; tx+=$10} END {printf \"%d %d\", rx+0, tx+0}' "
    "/proc/net/dev"
)
CMD_PORTS = "ss -lntuH 2>/dev/null | head -n 40 || netstat -lntu 2>/dev/null | head -n 40"
CMD_PROCS = "ps -eo pid,user,pcpu,pmem,comm --sort=-pcpu | head -n 16"
CMD_NCPU = "nproc"


def parse_cpu(output: str) -> float:
    return float(output.strip() or 0)


def parse_memory(output: str) -> dict[str, float]:
    parts = output.strip().split()
    if len(parts) < 3:
        return {"percent": 0.0, "used_kb": 0.0, "total_kb": 0.0}
    return {
        "percent": float(parts[0]),
        "used_kb": float(parts[1]),
        "total_kb": float(parts[2]),
    }


def parse_load(output: str) -> dict[str, float]:
    parts = output.strip().split()
    return {
        "1m": float(parts[0]) if len(parts) > 0 else 0.0,
        "5m": float(parts[1]) if len(parts) > 1 else 0.0,
        "15m": float(parts[2]) if len(parts) > 2 else 0.0,
    }


def parse_uptime(output: str) -> int:
    return int(float(output.strip() or 0))


def parse_disk(output: str) -> dict[str, float]:
    parts = output.strip().split()
    if len(parts) < 3:
        return {"percent": 0.0, "used_kb": 0.0, "total_kb": 0.0}
    return {
        "percent": float(parts[0]),
        "used_kb": float(parts[1]),
        "total_kb": float(parts[2]),
    }


def parse_network(output: str) -> dict[str, int]:
    parts = output.strip().split()
    if len(parts) < 2:
        return {"rx_bytes": 0, "tx_bytes": 0}
    return {"rx_bytes": int(parts[0]), "tx_bytes": int(parts[1])}


def parse_ports(output: str) -> list[str]:
    lines = [ln.strip() for ln in output.splitlines() if ln.strip()]
    return lines[:40]


def parse_processes(output: str) -> list[dict[str, str]]:
    lines = [ln.rstrip() for ln in output.splitlines() if ln.strip()]
    if not lines:
        return []
    # Skip header
    body = lines[1:] if lines[0].lower().startswith("pid") else lines
    procs: list[dict[str, str]] = []
    for line in body[:15]:
        parts = re.split(r"\s+", line.strip(), maxsplit=4)
        if len(parts) < 5:
            continue
        procs.append(
            {
                "pid": parts[0],
                "user": parts[1],
                "cpu": parts[2],
                "mem": parts[3],
                "command": parts[4],
            }
        )
    return procs


def parse_ncpu(output: str) -> int:
    return max(int(output.strip() or 1), 1)


def collect_metrics(
    creds: SSHCredentials,
    *,
    connect: Callable[..., Any] = connect_ssh,
    run: Callable[..., str] = run_command,
) -> dict[str, Any]:
    """Connect once and gather all PRD metrics. Output treated as untrusted."""
    client = connect(creds)
    try:
        cpu = parse_cpu(run(client, CMD_CPU))
        memory = parse_memory(run(client, CMD_MEM))
        load = parse_load(run(client, CMD_LOAD))
        uptime = parse_uptime(run(client, CMD_UPTIME))
        disk = parse_disk(run(client, CMD_DISK))
        network = parse_network(run(client, CMD_NET))
        ports = parse_ports(run(client, CMD_PORTS))
        processes = parse_processes(run(client, CMD_PROCS))
        ncpu = parse_ncpu(run(client, CMD_NCPU))
    finally:
        client.close()

    return {
        "cpu_percent": cpu,
        "memory": memory,
        "load": load,
        "uptime_seconds": uptime,
        "disk": disk,
        "network": network,
        "ports": ports,
        "processes": processes,
        "cpu_count": ncpu,
        "error": None,
    }


def collect_metrics_safe(creds: SSHCredentials) -> dict[str, Any]:
    try:
        return collect_metrics(creds)
    except SSHError as exc:
        return {
            "cpu_percent": None,
            "memory": None,
            "load": None,
            "uptime_seconds": None,
            "disk": None,
            "network": None,
            "ports": [],
            "processes": [],
            "cpu_count": None,
            "error": str(exc),
        }
