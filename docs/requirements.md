# PRD: Demo Linux Server Monitoring (Local)

## 1. Overview

Local demo web app so internal L1/L2/L3 and app teams can view live Linux host metrics without logging into the server. Deploy and run only on the machine where Cursor is running. Scope is intentionally small for a demo.

## 2. Problem

Today, checking real-time memory, CPU, network, and port usage requires SSH/login to each server. This demo centralizes a read-only metrics UI for the local Linux host.

## 3. Users

- Internal L1, L2, L3 infrastructure teams
- Application development groups  
- Single shared demo account: `admin` (no multi-user management)

## 4. Goals (Demo)

- Sign in with hashed password
- Register the local Linux host for monitoring via SSH fields
- View metrics in a simple, friendly UI (metrics views are read-only)
- Manual refresh + short history charts
- Simple visual threshold warnings

## 5. Out of Scope

- Multi-user admin, roles, SSO
- Monitoring remote VMs / other network hosts
- Agents, Docker, production HA, alerting notifications (email/Slack)
- Non-Linux OS
- Auto-refresh / streaming

## 6. Tech Stack

| Layer | Choice |
|-------|--------|
| Backend | Python + Flask |
| Frontend | Flask templates + CSS/JS (attractive, simple UI) |
| DB | Local SQLite |
| Collection | SSH from the app to the monitored host |
| Run | Single process: `python app.py` (or `flask run`) |

## 7. Features

### 7.1 Sign-in

- Default username: `admin`
- Default password: `admin` (store only a hash, e.g. bcrypt; never plaintext in DB)
- Session required for all pages except login
- No “add user” in this demo

### 7.2 Add server (local host)

Provision to add a Linux server with:

| Field | Required |
|-------|----------|
| Hostname / IP | Yes (demo: typically `127.0.0.1` or `localhost`) |
| Display name | Yes |
| SSH port | Yes (default `22`) |
| SSH username | Yes |
| SSH password **or** key path | Yes (one of the two) |

- Target: **only** the machine where the app/Cursor runs (local host).
- Metrics UI remains read-only; add/edit server is config only for the demo admin.

### 7.3 Metrics (per server detail)

On manual refresh, collect and show:

- CPU usage
- Memory usage
- Network usage
- Port usage / listening ports
- Disk usage
- Process list
- Uptime
- Load average

### 7.4 Navigation & UX

- Friendly UI, metrics in **read-only** mode
- Flow: **Server list → Server detail**
- **Manual refresh only** (button); no auto-refresh
- Short history charts (last **15–60 minutes** of collected samples stored in SQLite)
- Simple **visual warnings** when thresholds are crossed (e.g. highlight/badge). Suggested defaults for demo:
  - CPU ≥ 80%
  - Memory ≥ 85%
  - Disk ≥ 90%
  - Load average (1m) ≥ CPU count

### 7.5 Data

- SQLite stores: admin password hash, server connection fields, metric samples for short history
- SSH credentials stored only as needed for local demo (keep simple; document that this is not production-safe)

## 8. Local run (minimal)

1. Create a Python venv and install dependencies (`flask`, SSH client lib, bcrypt, etc.).
2. Ensure local SSH access works for the configured user (password or key) to `localhost`.
3. Start: `python app.py` (or `flask run`).
4. Open the app in a browser (e.g. `http://127.0.0.1:5000`).
5. Sign in as `admin` / `admin`, add the local host, open it, click Refresh.

## 9. Acceptance criteria (demo)

- [x] Login works with `admin` / `admin`; password is hashed at rest
- [x] Can add a local Linux server with the fields in §7.2
- [x] Server list links to a detail page
- [x] Detail page shows all metrics in §7.3 after manual refresh
- [x] History charts show recent samples (15–60 min window)
- [x] Threshold crossings show a clear visual warning
- [x] Metrics views do not allow mutating host state
- [x] App runs as a single local Flask process with SQLite

## 10. Non-goals reminder

This is a **demo** for local use only—minimal steps, no production hardening beyond hashed login password.
