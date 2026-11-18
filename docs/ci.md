# CI

GitHub Actions workflow: `.github/workflows/ci.yml`

## What it does

On push/PR to `main` (or `master`):

1. Checkout the repo  
2. Install Python **3.10** (matches local demo)  
3. `pip install -r requirements-dev.txt`  
4. Run `pytest -q` with ephemeral env `SECRET_KEY` (not logged as a secret value beyond normal env injection)

## Local equivalent

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

No production secrets are required for CI. Tests use temporary SQLite DBs and must not print passwords or write real credential files.
