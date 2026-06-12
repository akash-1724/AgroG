## 1. Backend Automated Tests

- [x] 1.1 Create automated tests file `backend/app/tests/test_backend.py` covering health, user authentication, RBAC authorization, listings, orders, nearby farmers, and assistant fallback.
- [x] 1.2 Add pytest and testing dependencies to `backend/requirements.txt`.
- [x] 1.3 Configure a separate test database configuration or sqlite database path in backend settings for safe isolated local/CI testing.

## 2. ML Service Automated Tests

- [x] 2.1 Create automated tests file `ml_service/tests/test_ml.py` verifying model parameter validation, health, model-status responses, 5MB upload validation, and baseline/demo fallbacks.
- [x] 2.2 Add test commands execution instructions inside `ml_service/README.md`.

## 3. GitHub Actions CI Configuration

- [x] 3.1 Create GitHub Actions workflow file `.github/workflows/ci.yml`.
- [x] 3.2 Implement backend verification steps (install deps, run pytest).
- [x] 3.3 Implement frontend verification steps (install deps, run compile/typecheck, run build check).
- [x] 3.4 Implement ML service checks (install deps, run unit tests).

## 4. Production Readiness & Deployment Documentation

- [x] 4.1 Create `docs/deployment.md` covering frontend, backend, PostgreSQL database, and Redis hosting.
- [x] 4.2 Create `docs/production-readiness.md` containing final checklists, environment secrets checklist, rollback strategy, and limitations.
- [x] 4.3 Update the main root `README.md` to outline local test verification commands.
