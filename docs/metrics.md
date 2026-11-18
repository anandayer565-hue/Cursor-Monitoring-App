# Metrics collection

Manual refresh only. The app SSHes to **localhost** and runs **fixed** read-only commands (no user-controlled shell interpolation). SSH output is treated as untrusted and HTML-escaped in templates.

## Commands

| Metric | Command (fixed) |
|--------|-----------------|
| CPU % | `grep 'cpu ' /proc/stat` + awk |
| Memory | awk on `/proc/meminfo` |
| Load | `cat /proc/loadavg` |
| Uptime | `cut -d. -f1 /proc/uptime` |
| Disk `/` | `df -P /` |
| Network | sum RX/TX from `/proc/net/dev` |
| Ports | `ss -lntuH` (fallback `netstat`) |
| Processes | `ps -eo pid,user,pcpu,pmem,comm --sort=-pcpu \| head` |
| CPU count | `nproc` |

## History

Samples are stored in SQLite (`metric_samples`) and pruned to the last **60 minutes** by default (`HISTORY_RETENTION_MINUTES`).

## Threshold warnings (display-only)

| Check | Warn when |
|-------|-----------|
| CPU | ≥ 80% |
| Memory | ≥ 85% |
| Disk | ≥ 90% |
| Load (1m) | ≥ CPU count |

Warnings never trigger remote actions.

## Local SSH setup (minimal)

1. Ensure `sshd` is running on this machine.  
2. Confirm you can `ssh <user>@127.0.0.1` with password or key.  
3. In the UI, add server with hostname `127.0.0.1` (or `localhost` / `::1`), port `22`, your username, and password **or** key path.

**Demo risk:** SSH password/key path may be stored in local SQLite — not production-safe.
