## Why

AgroGuide has completed its planned feature phases and now needs a final end-to-end quality audit before it is considered stable. This phase exists to find and fix correctness, security, documentation, verification, and deployment-readiness gaps without adding product features or redesigning the app.

## What Changes

- Add a controlled audit plan covering backend, frontend, ML service, database/migrations, auth/RBAC, marketplace/cart/orders/fulfillment, farmer profiles/reviews/ratings, advisory/weather/price/history, educational resources/location/assistant, admin analytics, image upload, environment/secrets, Docker, testing/CI, documentation/deployment, and OpenSpec consistency.
- Define prioritization rules for findings: P0, P1, P2, and P3.
- Define implementation guardrails for the apply phase: fix P0/P1 issues, fix only small safe localized P2 issues, and document large P2/P3 items instead of implementing them.
- Produce a final audit report structure and verification command list.
- Require verification that core services start, tests/checks are run or failures are documented, migrations work, no real secrets are committed, and OpenSpec state is clean.
- Do not add new product features, paid services, payment gateway, broad UI redesign, repository restructuring, or new deployment architecture.

## Capabilities

### New Capabilities
- `final-quality-audit`: Defines the final audit process, priorities, required coverage areas, verification commands, report structure, acceptance criteria, and out-of-scope constraints.

### Modified Capabilities
- `testing`: Adds final audit verification expectations across backend tests, ML tests, frontend lint/type/build, Docker config, migrations, and documented failure handling.
- `educational-resources`: Clarifies that final audit must verify educational resource CRUD and publish/draft visibility rather than add new content features.
- `auth-and-rbac`: Clarifies final audit expectations for registration/login/logout/refresh/me, admin registration control, roles, backend RBAC, ownership checks, and no frontend-only security assumptions.

## Impact

- Planning artifacts under `openspec/changes/final-quality-audit/`.
- Main audit execution will inspect existing code under `backend/`, `frontend/`, `ml_service/`, `openspec/`, `docker-compose.yml`, docs, env examples, and CI workflows.
- Apply phase may make small targeted fixes only for P0/P1 and safe localized P2 issues discovered during audit.
- No new runtime dependencies, paid integrations, product features, repo structure changes, or broad redesigns are intended.
