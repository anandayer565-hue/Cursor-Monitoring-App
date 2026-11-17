# Demo Linux Server Monitoring

Local-only demo Flask app for viewing Linux host metrics (CPU, memory, network, ports, disk, processes, uptime, load) without logging into the server for every check.

**Audience:** internal L1 / L2 / L3 and app teams  
**Scope:** runs on the machine where Cursor is running; monitors **localhost** only  
**Status:** Phase 1 — sign-in with hashed password + protected UI

## Quick start

```bash
cd "/home/jumpuser9/Desktop/Monitoring Application"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) → you will be redirected to **Sign in**.

Optional: copy `.env.example` to `.env` and set `SECRET_KEY` (Flask sessions + CSRF).

## Sign in

| Field | Value |
|-------|--------|
| Username | `admin` |
| Password | `admin` |

Only a **bcrypt hash** is stored in SQLite (`instance/monitor.db`). Plaintext is never saved.

On first run the app creates the DB and seeds `admin` if missing. Delete `instance/monitor.db` to re-seed on next start.

Login and logout forms require a **CSRF token** (Flask-WTF). Browsers get this automatically from the form; raw POSTs without a token are rejected (HTTP 400).

## Routes (current)

| Path | Auth | Description |
|------|------|-------------|
| `GET/POST /login` | public | Sign in |
| `POST /logout` | required | Sign out (CSRF-protected) |
| `GET /` | required | Home |
| `GET /servers` | required | Server list (empty until registration) |
| `GET /servers/<id>` | required | Stub detail (read-only placeholders) |

## Database

- File: `instance/monitor.db` (gitignored)
- Table `users`: `username`, `password_hash`

## Tests

```bash
source .venv/bin/activate
pytest
```

## Security notes (demo)

- Do not commit `.env`, `*.db`, or SSH keys (see `.gitignore`).
- `SECRET_KEY` should come from the environment for anything beyond a throwaway local run.
- Passwords are checked via bcrypt (constant-time); failures show only “Invalid credentials.”
- CSRF on state-changing forms; sessions for auth.
- Metric views are **read-only**; the UI must not mutate host state.
- This is **not** production-hardened.

## Docs

- [docs/requirements.md](docs/requirements.md) — PRD  
- [docs/TODO.md](docs/TODO.md) — implementation checklist  
