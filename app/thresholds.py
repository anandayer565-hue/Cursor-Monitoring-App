"""Display-only threshold checks for demo warnings."""

from __future__ import annotations

from typing import Any

# PRD defaults
CPU_WARN = 80.0
MEMORY_WARN = 85.0
DISK_WARN = 90.0


def evaluate_warnings(metrics: dict[str, Any] | None) -> dict[str, bool]:
    """Return warn flags. Never triggers remote actions."""
    if not metrics or metrics.get("error"):
        return {
            "cpu": False,
            "memory": False,
            "disk": False,
            "load": False,
        }

    cpu = metrics.get("cpu_percent")
    mem = (metrics.get("memory") or {}).get("percent")
    disk = (metrics.get("disk") or {}).get("percent")
    load_1m = (metrics.get("load") or {}).get("1m")
    cpu_count = metrics.get("cpu_count") or 1

    return {
        "cpu": cpu is not None and float(cpu) >= CPU_WARN,
        "memory": mem is not None and float(mem) >= MEMORY_WARN,
        "disk": disk is not None and float(disk) >= DISK_WARN,
        "load": load_1m is not None and float(load_1m) >= float(cpu_count),
    }


def any_warning(warnings: dict[str, bool]) -> bool:
    return any(warnings.values())
