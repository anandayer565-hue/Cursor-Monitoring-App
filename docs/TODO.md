# TODO: Demo Linux Server Monitoring

Small, AI-friendly increments. Complete each step (code + security + docs + tests where noted) before starting the next. Local demo only — keep steps minimal.

Reference: [requirements.md](./requirements.md)

---

## Phase 0 — Project initialization and Basic UI

### Step 0.1 — Scaffold the Flask app
- [x] Create project layout (`app/`, `templates/`, `static/`, `tests/`, `docs/`)
- [x] Add `requirements.txt` with pinned demo deps (`flask`, etc.)
- [x] Add `.gitignore` (venv, `__pycache__`, `.env`, `*.db`, secrets)
- [x] **Security:** Do not commit secrets, `.env`, or SQLite DB files
- [x] **Docs:** Add a short `README.md` (what it is, local-only demo)

### Step 0.2 — Basic UI shell
- [x] Create base template (nav, layout, simple attractive CSS)
- [x] Add home/placeholder page route (`GET /`)
- [x] Wire static CSS/JS; confirm page loads via `python app.py`
- [x] **Security:** Set a placeholder `SECRET_KEY` from env (not hardcoded for later sessions)
- [x] **Docs:** Note in `README.md` how to start and open `http://127.0.0.1:5000`

### Step 0.3 — Empty server list page (UI only, no DB yet)
- [x] Add `/servers` page with empty list + “Add server” button (disabled or linked to stub)
- [x] Add stub server detail page template (static placeholders for metrics)
- [x] **Security:** Mark metrics areas as read-only in UI copy
- [x] **Docs:** Update `docs/requirements.md` acceptance notes if UI routes change; keep `README` routes list current

---

## Phase 1 — Sign-in and unit tests

### Step 1.1 — Password hashing helpers
- [x] Add bcrypt (or equivalent) dependency
- [x] Implement `hash_password` / `check_password` helpers
- [x] **Security:** Never store or log plaintext passwords; use a slow hash (bcrypt)
- [x] **Docs:** Document default demo creds (`admin` / `admin`) and that only the hash is stored
- [x] **Tests:** Unit tests for hash + verify (match / mismatch)

### Step 1.2 — SQLite user bootstrap
- [x] Init SQLite + `users` table (username, password_hash)
- [x] On first run, seed `admin` with hashed password `admin`
- [x] **Security:** Ensure seed uses hash only; DB file stays local and gitignored
- [x] **Docs:** Document DB file location and re-seed behavior
- [x] **Tests:** Unit test that seeded hash verifies against `admin`

### Step 1.3 — Login / logout routes
- [x] `GET/POST /login` form (username + password)
- [x] Session-based auth after successful login; `POST /logout`
- [x] Protect `/` and `/servers` (redirect to login if unauthenticated)
- [x] **Security:** Use Flask sessions with `SECRET_KEY` from env; constant-time password check via library; no password in flash/logs
- [x] **Docs:** Update `README` with login steps
- [x] **Tests:** Unit/route tests — bad password fails; good password sets session; logout clears session; protected route redirects

### Step 1.4 — Login UI polish
- [x] Style login page consistently with base UI
- [x] Show safe error message on failure (no user enumeration detail beyond “invalid credentials”)
- [x] **Security:** CSRF protection for forms (Flask-WTF or equivalent minimal approach)
- [x] **Docs:** Note CSRF requirement briefly in `README` or `docs/`
- [x] **Tests:** Confirm login POST without valid CSRF token is rejected (if CSRF enabled)

---

## Phase 2 — CI/CD (GitHub Actions) early

### Step 2.1 — Test runner locally
- [x] Add `pytest` (+ Flask test client helpers) to `requirements.txt` / `requirements-dev.txt`
- [x] Ensure `pytest` passes for Phase 1 tests
- [x] **Security:** Tests must not print secrets or write real credential files
- [x] **Docs:** Add “Run tests” one-liner to `README`

### Step 2.2 — GitHub Actions workflow
- [x] Add `.github/workflows/ci.yml` (install deps, run `pytest` on push/PR)
- [x] Use Python version matching local demo
- [x] **Security:** No secrets in workflow logs; use ephemeral CI env `SECRET_KEY`
- [x] **Docs:** Short `docs/ci.md` or `README` section describing the CI job

---

## Phase 3 — Server registry (local host only)

### Step 3.1 — Servers table and model
- [x] SQLite `servers` table: display name, hostname/IP, SSH port, username, auth (password **or** key path)
- [x] **Security:** Restrict hostname to localhost/`127.0.0.1` only (demo rule); reject other hosts
- [x] **Docs:** Document localhost-only constraint
- [x] **Tests:** Unit tests for localhost allow / remote reject

### Step 3.2 — Add server form (authenticated)
- [x] `GET/POST /servers/new` with required fields from PRD
- [x] Validate: port range, require password **or** key path (not neither)
- [x] Redirect to server list on success
- [x] **Security:** Auth required; CSRF; never echo SSH password back into HTML value attributes after save; prefer not logging credentials
- [x] **Docs:** Document fields and localhost examples in `README`
- [x] **Tests:** Validation tests (missing fields, non-localhost, missing auth method)

### Step 3.3 — Server list (live data)
- [x] Render saved servers; link each to detail route
- [x] Empty state message when none exist
- [x] **Security:** Auth required; do not display SSH password on list
- [x] **Docs:** Update screenshots/notes if needed (optional for demo)
- [x] **Tests:** List shows created server display name

---

## Phase 4 — SSH collector (read-only commands)

### Step 4.1 — SSH client wrapper
- [x] Add Paramiko (or similar); connect to localhost with password or key
- [x] Connection timeout and clear error handling
- [x] **Security:** Read-only remote commands only; no shell writes; disable agent forwarding; document demo credential risk
- [x] **Docs:** Minimal SSH setup for local user (`sshd`, key or password)
- [x] **Tests:** Mock SSH unit tests for connect success/failure

### Step 4.2 — Metric command runners (one metric family at a time)
- [x] Implement collectors: CPU, memory, load average, uptime
- [x] Implement collectors: disk, network, listening ports, process list
- [x] Parse into simple dict/structures
- [x] **Security:** Use fixed command strings (no user-controlled shell interpolation); treat output as untrusted data when rendering
- [x] **Docs:** List commands used in `docs/metrics.md` (short)
- [x] **Tests:** Parser unit tests with sample command output fixtures

### Step 4.3 — Manual refresh on detail page
- [x] Server detail loads last known data; **Refresh** button triggers SSH collect
- [x] Persist a metric sample snapshot to SQLite with timestamp
- [x] **Security:** Auth required; refresh is read-only; rate-limit lightly if easy (optional for demo)
- [x] **Docs:** Document manual-refresh behavior
- [x] **Tests:** Mocked refresh stores a sample; unauthenticated refresh redirected

---

## Phase 5 — Detail UI, history, warnings

### Step 5.1 — Read-only metrics display
- [x] Render all PRD metrics on detail page (tables/cards)
- [x] No edit controls for metric values
- [x] **Security:** Escape all SSH-derived strings in templates (auto-escape on)
- [x] **Docs:** Map UI sections to PRD §7.3
- [x] **Tests:** Detail page smoke test with mocked metrics

### Step 5.2 — Short history storage + charts
- [x] Keep samples for last 15–60 minutes; prune older rows
- [x] Simple charts (CPU/memory/disk or similar) from stored samples
- [x] **Security:** Auth required for history API/data endpoints
- [x] **Docs:** Document retention window
- [x] **Tests:** Prune logic unit test; history returns only recent points

### Step 5.3 — Visual threshold warnings
- [x] Apply demo thresholds (CPU ≥80%, memory ≥85%, disk ≥90%, load 1m ≥ CPU count)
- [x] Badges/highlights on detail (and optional list indicators)
- [x] **Security:** Thresholds are display-only (no remote actions)
- [x] **Docs:** Document default thresholds in `docs/metrics.md`
- [x] **Tests:** Unit tests for warn / ok boundary values

---

## Phase 6 — Hardening pass (still demo-minimal) + docs freeze

### Step 6.1 — Config and secrets cleanup
- [x] Load `SECRET_KEY` and DB path from environment with safe local defaults
- [x] Confirm `.gitignore` covers DB, venv, `.env`
- [x] **Security:** README warns: demo only; SSH creds in SQLite are not production-safe
- [x] **Docs:** Final local run steps (venv, install, run, login, add localhost, refresh)

### Step 6.2 — Acceptance checklist
- [x] Walk PRD §9 acceptance criteria and check each box in `requirements.md`
- [x] Ensure CI still green
- [x] **Security:** Quick review — auth on all non-login routes; localhost-only; hashed admin password; no metric mutation
- [x] **Docs:** `README.md` + `docs/TODO.md` reflect completed state

---

## Suggested order (summary)

1. Phase 0 — Init + Basic UI  
2. Phase 1 — Sign-in + unit tests  
3. Phase 2 — CI (GitHub Actions)  
4. Phase 3 — Add/list local server  
5. Phase 4 — SSH collect + manual refresh  
6. Phase 5 — UI detail, history charts, warnings  
7. Phase 6 — Demo hardening + docs freeze  

Work **one checkbox group (step) at a time**.
