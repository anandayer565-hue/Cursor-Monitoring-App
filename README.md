# Demo Linux Server Monitoring

Local-only demo Flask app for viewing Linux host metrics (CPU, memory, network, ports, disk, processes, uptime, load) without logging into the server for every check.

**Audience:** internal L1 / L2 / L3 and app teams  
**Scope:** runs on the machine where Cursor is running; monitors **localhost only**  
**Status:** Phases 0–6 complete (local demo)

## Quick start

```bash
cd "/home/jumpuser9/Desktop/Monitoring Application"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) → sign in → **Add server** (`127.0.0.1`) → open detail → **Refresh**.

Optional: copy `.env.example` to `.env` and set `SECRET_KEY` / `DATABASE_PATH` / `HISTORY_RETENTION_MINUTES`.

## Sign in

| Field | Value |
|-------|--------|
| Username | `admin` |
| Password | `admin` |

Only a **bcrypt hash** is stored in SQLite (`instance/monitor.db`).

## Add a server (localhost only)

Required fields: display name, hostname/IP (`localhost` / `127.0.0.1` / `::1`), SSH port (default 22), SSH username, and **SSH password or key path**.

Remote hosts are rejected. SSH credentials in SQLite are **not production-safe**.

## Routes

| Path | Auth | Description |
|------|------|-------------|
| `GET/POST /login` | public | Sign in (CSRF) |
| `POST /logout` | required | Sign out (CSRF) |
| `GET /` | required | Home |
| `GET /servers` | required | Server list (no passwords shown) |
| `GET/POST /servers/new` | required | Add server |
| `GET/POST /servers/<id>` | required | Detail + manual Refresh |

## Metrics

Manual refresh over SSH (read-only fixed commands). History charts for the last **60 minutes**. Visual warnings: CPU ≥80%, memory ≥85%, disk ≥90%, load 1m ≥ CPU count.

See [docs/metrics.md](docs/metrics.md).

## Database

- File: `instance/monitor.db` (gitignored) or `DATABASE_PATH`
- Tables: `users`, `servers`, `metric_samples`

## Tests / CI

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

GitHub Actions runs the same on push/PR — see [docs/ci.md](docs/ci.md).

## Security notes (demo)

- Do not commit `.env`, `*.db`, or SSH keys.
- `SECRET_KEY` from environment when possible.
- CSRF on forms; bcrypt login; localhost-only monitoring; metrics are read-only.
- **Not** production-hardened.

## Docs

- [docs/requirements.md](docs/requirements.md) — PRD  
- [docs/TODO.md](docs/TODO.md) — checklist  
- [docs/ci.md](docs/ci.md) — CI  
- [docs/metrics.md](docs/metrics.md) — collectors & thresholds  
