## Context

The current repository contains the following known issues:
- `backend/app/api/v1/api.py` is missing `APIRouter` import, which will prevent backend from starting.
- `docker-compose.yml` has hardcoded postgres password and JWT secrets, which is a security risk.
- casing mismatch: `SENTRY_DSN` is used in some configs while others reference `sentry_dsn`.
- ML service contains pillow-based mock heuristics that simulate ML prediction but this is not clearly highlighted in documentation.
- The monorepo needs unified local run guides and quick health endpoints.

## Goals / Non-Goals

**Goals:**
- Resolve backend imports and start FastAPI successfully.
- Clean Sentry casing to unified uppercase `SENTRY_DSN`.
- Extract hardcoded credentials from compose to safe environment variables.
- Add `/health` checks on both backend and ML services.
- Provide a robust developer setup instruction README.

**Non-Goals:**
- Implementing any new user stories or database models.
- Changing database migrations or application routing paths.

## Decisions

### 1. Backend Import & Route Fix
- Import `APIRouter` inside `backend/app/api/v1/api.py`.
- Add a GET `/health` route to `backend/app/main.py` that checks DB connection availability and returns status.

### 2. Environment Variables & Security
- Extract `POSTGRES_PASSWORD`, `JWT_SECRET`, `JWT_REFRESH_SECRET` from `docker-compose.yml` and bind them to host environment values.
- Clean `.env.example` to ensure dummy values are used as placeholders.
- Align all code reference lookups to use uppercase `SENTRY_DSN`.

### 3. ML Service Health & Mock Documentation
- Add a GET `/health` route to `ml_service/main.py`.
- Add docstrings to `ml_service/utils/disease_classifier.py` clearly explaining that it is currently running in mock heuristic mode for developer baseline testing.

## Risks / Trade-offs

- **[Risk] Sentry SDK initialization fails without network connectivity** -> *Mitigation*: Ensure Sentry SDK wraps calls in try/except blocks or ignores connection errors silently.
- **[Risk] Docker Compose fails if local env variables are unset** -> *Mitigation*: Provide default fallback configurations inside `docker-compose.yml` so it starts up out-of-the-box.
