## 1. Audit Setup and Baseline

- [x] 1.1 Confirm repository structure remains `frontend/`, `backend/`, `ml_service/`, `openspec/`, and `docker-compose.yml` without introducing new top-level application roots.
- [x] 1.2 Confirm all previous OpenSpec changes are archived/synced or explicitly explain any active changes.
- [x] 1.3 Create `docs/final-quality-audit.md` with sections for executive summary, scope, prioritization rules, findings, fixes, verification results, environment/secrets, deployment readiness, OpenSpec status, known limitations, and final assessment.
- [x] 1.4 Record audit prioritization rules in the report: P0, P1, P2, and P3.
- [x] 1.5 Establish apply-phase rule in the report: fix P0/P1, fix only small safe localized P2, document large P2/P3.
- [x] 1.6 Capture initial `git status --short` and `git diff --stat` summary in the report without reverting unrelated worktree changes.
- [x] 1.7 Inventory existing docs, env examples, CI workflow files, and OpenSpec active/archive state before making fixes.

## 2. Backend Correctness Audit

- [x] 2.1 Verify FastAPI app imports and starts without router/schema import errors.
- [x] 2.2 Verify all API routers are registered under expected prefixes and no intended router is missing.
- [x] 2.3 Review request/response schemas for invalid defaults, mismatched field names, and frontend/backend contract drift.
- [x] 2.4 Review consistent error responses for auth failures, validation failures, not-found, forbidden, and service-unavailable cases.
- [x] 2.5 Check for circular imports or import-time side effects that can break startup.
- [x] 2.6 Review async SQLAlchemy usage for lazy-load-in-async bugs, double commits, rollback gaps, and transaction consistency.
- [x] 2.7 Verify pagination/search/filter query validation on listing, review, resource, price, history, and discovery endpoints where applicable.
- [x] 2.8 Verify health/readiness endpoints for backend and document gaps if readiness is not implemented.
- [x] 2.9 Fix P0/P1 backend issues found, and document non-fixed P2/P3 backend findings.

## 3. Database and Migration Audit

- [x] 3.1 Verify Alembic config points to the intended metadata and environment variables.
- [x] 3.2 Verify all SQLAlchemy models are imported into migration metadata.
- [x] 3.3 Verify migrations can run from an empty database or document the exact blocker.
- [x] 3.4 Verify migration-created schema matches models for carts, reviews, intelligence, listing images, order item status fields, users, resources, and recommendations.
- [x] 3.5 Verify indexes/constraints exist for frequent ownership and lookup queries where practical.
- [x] 3.6 Verify status/enum values are consistent between models, schemas, endpoints, frontend types, tests, and OpenSpec.
- [x] 3.7 Fix P0/P1 migration/database issues found, and document non-fixed P2/P3 findings.

## 4. Auth, RBAC, and Ownership Audit

- [x] 4.1 Verify registration, login, logout, refresh-token rotation/revocation, and `/me` flows.
- [x] 4.2 Verify public Admin registration is controlled and roles are limited to farmer, customer, and admin.
- [x] 4.3 Verify protected backend endpoints enforce backend RBAC rather than relying on frontend guards.
- [x] 4.4 Verify farmer listing ownership checks.
- [x] 4.5 Verify customer cart and order ownership checks.
- [x] 4.6 Verify farmer order item fulfillment ownership checks and Admin override.
- [x] 4.7 Verify review eligibility, ownership, self-review blocking, and Admin moderation authorization.
- [x] 4.8 Verify recommendation history ownership and deletion authorization.
- [x] 4.9 Verify admin-only analytics and admin-only resource management behavior.
- [x] 4.10 Fix P0/P1 auth/RBAC/ownership issues found, and document non-fixed P2/P3 findings.

## 5. Marketplace, Cart, Orders, Profiles, and Reviews Audit

- [x] 5.1 Verify cart flow is required before checkout and direct marketplace checkout is blocked or safely redirected.
- [x] 5.2 Verify checkout validates listing status and stock before creating orders.
- [x] 5.3 Verify order item price snapshots are stored and stock is deducted transaction-safely.
- [x] 5.4 Verify multi-farmer order display and item-level fulfillment behavior for Customers, Farmers, and Admins.
- [x] 5.5 Verify stock restoration rules for rejected/cancelled order items avoid double restoration.
- [x] 5.6 Verify invalid order/order-item status transitions are blocked.
- [x] 5.7 Verify public listing browsing and farmer profiles do not expose private data.
- [x] 5.8 Verify public farmer profiles show active listings, approximate location, computed rating average/count, and recent reviews.
- [x] 5.9 Verify duplicate/ineligible reviews are blocked and farmers cannot review themselves.
- [x] 5.10 Fix P0/P1 commerce/profile/review issues found, and document non-fixed P2/P3 findings.

## 6. Advisory ML, Weather, Prices, History, Content, Location, and Assistant Audit

- [x] 6.1 Verify ML service starts and health/model-status endpoint behavior is accurate.
- [x] 6.2 Verify missing ML model artifacts do not crash the service and demo/baseline mode is clearly marked.
- [x] 6.3 Verify crop and fertilizer recommendation input validation.
- [x] 6.4 Verify disease detection image type and size validation.
- [x] 6.5 Verify weather-aware recommendation fallback behavior and visible disclosure.
- [x] 6.6 Verify price trend data is not falsely presented as live if sample/demo data is used.
- [x] 6.7 Verify recommendation history is user-scoped and delete authorization is correct.
- [x] 6.8 Verify advisory disclaimers are visible where needed.
- [x] 6.9 Verify educational resources CRUD, published/draft visibility, and Admin-only management.
- [x] 6.10 Verify farmer location privacy and nearby farmer discovery behavior.
- [x] 6.11 Verify assistant fallback mode, missing provider key behavior, safety handling, and absence of hardcoded provider API keys.
- [x] 6.12 Fix P0/P1 advisory/content/location/assistant issues found, and document non-fixed P2/P3 findings.

## 7. Admin, Media, Analytics, Frontend, and UX Audit

- [x] 7.1 Verify admin analytics uses real database records and is Admin-only.
- [x] 7.2 Verify Cloudinary upload is backend-only and secrets are not exposed to frontend environment variables or browser code.
- [x] 7.3 Verify image MIME, extension, and size validation plus missing Cloudinary config handling.
- [x] 7.4 Verify uploaded images appear in listing cards/details and listing create/edit flows handle errors without losing form state.
- [x] 7.5 Verify default Next.js starter content is removed.
- [x] 7.6 Verify required frontend routes render or document missing/broken routes.
- [x] 7.7 Verify role-aware navigation and protected route redirect/block behavior.
- [x] 7.8 Verify frontend API base URL uses environment configuration.
- [x] 7.9 Verify loading, error, empty, and unauthorized states on major flows.
- [x] 7.10 Verify form validation coverage on auth, listings, cart/order actions, reviews, recommendations, resources, and location/profile forms.
- [x] 7.11 Verify responsive layout is acceptable on desktop and mobile-sized viewports by inspection or documented limitation.
- [x] 7.12 Fix P0/P1 admin/media/frontend issues found, and document non-fixed P2/P3 findings.

## 8. Environment, Secrets, Docker, CI, and Documentation Audit

- [x] 8.1 Verify `.env.example` is complete, safe, and does not contain real secrets.
- [x] 8.2 Verify `.env` and secret-bearing local files are ignored by git.
- [x] 8.3 Search for committed real-looking secrets in source, docs, workflows, and config; document rotation recommendation if any are found.
- [x] 8.4 Verify JWT, DB, Cloudinary, Google OAuth, Sentry, Gemini/OpenAI, Redis, and ML service variables are documented and can be blank when optional.
- [x] 8.5 Verify `docker-compose.yml` uses env variables safely enough for local development and document production hardening gaps.
- [x] 8.6 Verify PostgreSQL, Redis, backend, ML service, and frontend can start locally through Docker or document blocker.
- [x] 8.7 Verify README setup instructions match real commands.
- [x] 8.8 Verify API docs or endpoint list exists or document gap.
- [x] 8.9 Verify deployment docs and final production readiness checklist exist or add small safe documentation.
- [x] 8.10 Verify known limitations are documented: demo ML mode, optional Sentry, optional Google OAuth, free-tier deployment limits, sample price data if used, and Cloudinary optionality.
- [x] 8.11 Verify GitHub Actions workflow exists, does not require real external secrets, and uses current project paths.
- [x] 8.12 If CI workflow is missing, classify it as P2 and either add a small existing-command workflow or document the missing workflow with recommended commands.
- [x] 8.13 Fix P0/P1 environment/secrets/Docker/CI/docs issues found, fix small safe localized P2 documentation gaps, and document larger P2/P3 findings.

## 9. Verification Commands

- [x] 9.1 Run `git status --short` and `git diff --stat` and record summarized results.
- [x] 9.2 Run `cd backend && PYTHONPATH=. pytest app/tests/test_backend.py` or document blocker/failure.
- [x] 9.3 Run `cd ml_service && PYTHONPATH=.. pytest tests/test_ml.py` or document blocker/failure.
- [x] 9.4 Run `cd frontend && npm run lint` or document blocker/failure.
- [x] 9.5 Run `cd frontend && npx tsc --noEmit` or document blocker/failure.
- [x] 9.6 Run `cd frontend && npm run build` or document blocker/failure.
- [x] 9.7 Run `cd backend && alembic upgrade head` or document blocker/failure.
- [x] 9.8 Run `docker compose config` or document blocker/failure without copying secrets into the report.
- [x] 9.9 Run `docker compose up -d --build` or document blocker/failure.
- [x] 9.10 Verify backend health endpoint after Docker startup or document blocker/failure.
- [x] 9.11 Verify ML health/model-status endpoint after Docker startup or document blocker/failure.
- [x] 9.12 Verify frontend root route after Docker startup or document blocker/failure.
- [x] 9.13 Run `openspec list --json` and document active changes status.
- [x] 9.14 Run `openspec validate --specs --strict` or document blocker/failure.

## 10. Final Report and OpenSpec Readiness

- [x] 10.1 Update `docs/final-quality-audit.md` with exact verification command results.
- [x] 10.2 Ensure every P0/P1 finding is fixed or documented as blocked with cause and recommendation.
- [x] 10.3 Ensure large P2/P3 findings are documented instead of implemented.
- [x] 10.4 Ensure no new product feature, paid service, payment gateway, broad redesign, repo restructuring, or new ML model was introduced.
- [x] 10.5 Ensure README/setup docs and `.env.example` changes, if any, are accurate and safe.
- [x] 10.6 Re-run targeted checks after any fixes and update the final report.
- [x] 10.7 Verify OpenSpec status is clean or remaining active changes are explained.
- [x] 10.8 Mark this task list accurately as audit work completes.
