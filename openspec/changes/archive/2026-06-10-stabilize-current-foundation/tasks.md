## 1. Code Fixes & Import Alignments

- [x] 1.1 Fix missing `APIRouter` import inside `backend/app/api/v1/api.py`
- [x] 1.2 Align Sentry environment variable casing to unified uppercase `SENTRY_DSN` in backend, frontend, and ML configurations
- [x] 1.3 Add backend health check endpoint (`/health` or `/api/v1/health`)
- [x] 1.4 Add ML service health check endpoint (`/health`)

## 2. Security & Configuration Cleanup

- [x] 2.1 Move hardcoded database passwords and JWT secrets out of `docker-compose.yml` into environment variables with safe defaults
- [x] 2.2 Clean `.env.example` to use dummy placeholders rather than developer configuration values

## 3. Documentation & Verification

- [x] 3.1 Document placeholder classification behavior of plant disease scanner in codebase and setup docs
- [x] 3.2 Add a root README.md containing monorepo structure description, startup instructions, and verification commands
- [x] 3.3 Spin up the Docker Compose stack to verify PostgreSQL, Redis, backend, ml_service, and frontend start successfully
