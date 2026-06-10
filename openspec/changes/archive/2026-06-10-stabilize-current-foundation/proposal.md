## Why

The existing AgroGuide repository scaffold contains several consistency, configuration, and runtime issues (such as missing package dependencies, hardcoded secrets in docker-compose.yml, casing mismatches in Sentry environment variables, and missing backend health check endpoints) that must be stabilized to ensure the application is reliable, secure, and verifiable.

## What Changes

This change focuses entirely on codebase stabilization and safety alignment, including:
- **Backend Cleanup**: Fix missing `APIRouter` import in `backend/app/api/v1/api.py` and implement a `/health` verification endpoint.
- **Config & Security Alignment**: Transition hardcoded database credentials and JWT secret tokens from `docker-compose.yml` to `.env` variables, clean `.env.example` to use safe placeholders, and unify Sentry variable casings.
- **ML Service Diagnostics**: Add a `/health` endpoint to the ML microservice and document fallback placeholder classification behaviors.
- **Documentation**: Provide a detailed README outlining exact local workspace initialization, Docker deployment, and verification check commands.

## Capabilities

### New Capabilities
<!-- None. This is a stabilization and cleanup proposal. No new user-facing capabilities are introduced. -->

### Modified Capabilities
<!-- None. No capability specification requirements are modified. -->

## Impact

- **Security**: Hardcoded secrets are moved to isolated, untracked environment files.
- **Reliability**: FastAPI startup errors are resolved, and minimum health probes are exposed.
- **Developer Experience**: Local run directions and verified startup scripts are clearly documented.
