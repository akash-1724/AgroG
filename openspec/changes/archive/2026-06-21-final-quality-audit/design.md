## Context

AgroGuide has completed the planned feature phases for authentication/RBAC, marketplace/cart/orders, farmer profiles/reviews, advisory ML/weather/prices/history, educational resources/location/assistant, admin analytics, backend-mediated listing media, and item-level fulfillment. The project should remain a small/time-pass project, but the final state should be clean, reliable, and production-style.

The repository structure must remain unchanged:
- `frontend/`
- `backend/`
- `ml_service/`
- `openspec/`
- `docker-compose.yml`

This is a final audit phase, not a feature-development phase. The audit must identify correctness, security, verification, documentation, deployment-readiness, and OpenSpec consistency gaps. During apply, only P0/P1 issues and small safe localized P2 issues should be fixed; larger P2/P3 findings should be documented in the final audit report.

## Goals / Non-Goals

**Goals:**
- Produce a prioritized final audit report for the full AgroGuide system.
- Verify backend correctness, frontend correctness, ML service behavior, migrations, Docker, testing, CI/CD, documentation, environment/secrets, deployment readiness, and OpenSpec consistency.
- Fix P0/P1 issues discovered during apply unless blocked.
- Fix small safe localized P2 issues when the change is low-risk.
- Document blocked P0/P1 issues and large P2/P3 issues with clear recommendations.
- Verify core commands and record exact results.
- Ensure no real secrets are committed and `.env.example` is safe and complete.

**Non-Goals:**
- No new product features.
- No app redesign or broad UI rewrite.
- No repository structure changes.
- No paid APIs, payment gateway, or new external paid services.
- No new ML models or retraining.
- No Google OAuth implementation unless it is already fully wired and only needs tiny cleanup.
- No deployment architecture redesign.
- No broad refactors unrelated to P0/P1 or small localized P2 fixes.

## Decisions

### Audit Output: Single Final Report

Create a final audit report at `docs/final-quality-audit.md` during apply. If a `docs/` directory does not exist, create it. The report should include:
- Executive summary.
- Current worktree and OpenSpec state at audit start.
- Audit scope.
- Prioritization rules.
- Findings grouped by P0/P1/P2/P3.
- Fixes applied during the audit.
- Blocked or deferred items.
- Verification command results.
- Environment/secrets review.
- Deployment readiness notes.
- OpenSpec consistency status.
- Known limitations.

Rationale: a single report keeps the final audit outcome reviewable and prevents scattering findings across comments or temporary files.

Alternative considered: only update README. Rejected because README should contain durable setup guidance, while the audit report should capture dated verification results and deferred findings.

Expected report skeleton:

```markdown
# Final Quality Audit

## Executive Summary
## Scope
## Worktree and OpenSpec State
## Prioritization Rules
## Findings
### P0
### P1
### P2
### P3
## Fixes Applied
## Deferred or Blocked Items
## Verification Results
## Environment and Secrets Review
## Docker and Deployment Readiness
## Documentation Review
## OpenSpec Consistency
## Known Limitations
## Final Assessment
```

### Prioritization Rules

Use these severities:
- P0: App cannot run, migrations cannot run, data loss risk, or serious credential/security exposure.
- P1: Core feature broken, auth/RBAC/ownership failure, incorrect checkout/order/review behavior, or backend/frontend contract breakage.
- P2: Important quality, test, CI, docs, deployment, or maintainability issue that does not break core flows.
- P3: Optional polish, cosmetic issue, low-risk cleanup, or future improvement.

Apply-phase fix rules:
- Fix P0 issues when feasible.
- Fix P1 issues when feasible.
- Fix small safe localized P2 issues.
- Document large P2 and all P3 issues unless explicitly approved later.
- If a P0/P1 issue cannot be fixed without a large redesign or missing external credentials, document the blocker and mitigation instead of inventing a new feature.

### Audit Methodology

Perform the audit in layers:
1. Preflight state capture: git status/diff summary, OpenSpec status, docs/CI/env file inventory, and existing known warnings.
2. Static structure and configuration review.
3. Backend import/router/schema/RBAC/database review.
4. Frontend route/build/API contract review.
5. ML service health/model fallback/input validation review.
6. Docker/env/secrets/CI/docs review.
7. OpenSpec status/spec implementation consistency review.
8. Verification command execution and report update.

Rationale: layering reduces risk by finding startup/configuration blockers before deeper flow testing.

Worktree safety rule: record existing modified/untracked files before fixes. Do not revert unrelated user changes. If a finding overlaps a file with unrelated edits, make the smallest compatible change and document it.

### Verification Commands

Run or document blockers for:
- `git status --short`
- `git diff --stat`
- `cd backend && PYTHONPATH=. pytest app/tests/test_backend.py`
- `cd ml_service && PYTHONPATH=.. pytest tests/test_ml.py`
- `cd frontend && npm run lint`
- `cd frontend && npx tsc --noEmit`
- `cd frontend && npm run build`
- `cd backend && alembic upgrade head`
- `docker compose config`
- `docker compose up -d --build`
- Backend health endpoint check.
- ML health/model-status endpoint checks where available.
- Frontend root route load check.
- `openspec list --json`
- `openspec validate --specs --strict`

If a command fails, classify the failure by priority, fix it if allowed by the apply-phase rules, then rerun. If not fixed, document exact failure and reason.

### Audit Coverage Checklist

The apply phase should check the following areas:
- Backend correctness: app startup, router imports, endpoint registration, schemas, error responses, circular imports, async SQLAlchemy usage, DB sessions, pagination/search/filter validation, health/readiness.
- Database/migrations: Alembic config, metadata imports, empty DB migration, indexes, status/enums, schema drift.
- Auth/RBAC: registration/login/logout/refresh/me, refresh revocation, admin registration control, role constraints, backend RBAC, ownership checks, no frontend-only security.
- Marketplace/cart/orders: cart-before-checkout, stock validation, price snapshots, multi-farmer orders, item fulfillment, stock restoration, transition blocking, public data exposure.
- Farmer profiles/reviews/ratings: public profile pages, active listing filtering, computed ratings, duplicate/ineligible reviews, self-review blocking, admin moderation.
- ML/advisory: service startup, model status, missing model fallback, demo mode labeling, crop/fertilizer/disease validation, weather fallback, price data labeling, recommendation history scope, disclaimers.
- Content/location/assistant: educational resource CRUD/visibility, location privacy, nearby farmer discovery, assistant fallback, missing provider key behavior, no hardcoded keys.
- Admin/media/analytics: real admin analytics, admin-only access, backend-only Cloudinary, frontend secret isolation, image validation, listing image display, missing config handling.
- Frontend: no default starter content, required routes render, role-aware navigation, protected routes, env-based API URL, loading/error/empty/unauthorized states, form validation, build, responsive acceptability.
- Environment/secrets: safe complete `.env.example`, `.env` ignored, no real secrets committed, no hardcoded JWT/DB/API secrets, optional Google/Sentry/Gemini/OpenAI variables safe when blank.
- Docker/local setup: compose env safety, Postgres/Redis/backend/ML/frontend startup, setup docs, health checks.
- Testing/CI: backend/ML/frontend checks, GitHub Actions workflow, no real external secrets required, CI commands match project structure, docs accurate.
- Documentation/deployment: README, endpoint docs/list, env docs, deployment docs, known limitations, production readiness checklist.
- OpenSpec: completed changes archived/synced, main specs reflect behavior, no half-finished active changes, task accuracy, no unimplemented claims.

### CI/CD Handling

If `.github/workflows/ci.yml` is missing, classify it as P2 unless the project cannot otherwise be verified locally. Add or update CI only if the workflow is small, uses existing commands, does not require real external secrets, and does not introduce new product behavior. Otherwise document the missing workflow and exact recommended commands in the final report.

### Documentation Updates

During apply, update documentation only where it improves accuracy or safety:
- README/setup commands.
- `.env.example` safety/completeness.
- Deployment/readiness docs if present or add a small checklist if absent.
- Final audit report.

Avoid turning documentation cleanup into a product redesign or broad rewrite.

## Risks / Trade-offs

- [Risk] Audit scope is large and can expand indefinitely. Mitigation: use the P0/P1/P2/P3 rules and document large non-critical issues instead of fixing everything.
- [Risk] Verification may expose real secrets in command output, especially Docker config. Mitigation: do not copy secrets into the report; document that secret-like values were present and recommend rotation if needed.
- [Risk] External integrations may fail due to missing keys. Mitigation: classify missing optional integrations as expected only if the app degrades gracefully and docs explain it.
- [Risk] Applying fixes can accidentally become feature work. Mitigation: every code change must map to an audit finding and priority.
- [Risk] Docker or migration checks may affect local state. Mitigation: prefer controlled local verification and document environment assumptions.

## Migration Plan

No planned schema or product migration is required for the audit itself. If the audit finds a migration issue, apply only minimal corrections needed for P0/P1 safety and validate with Alembic.

Rollback strategy:
- Revert small audit fixes if they introduce regressions.
- Keep the final report as documentation of what was checked and what remains.
- Do not alter persisted production data as part of this audit.

## Open Questions

- Which deployment target, if any, should deployment-readiness notes assume? Default: local Docker and generic free-tier readiness only.
- Should the apply phase run full Docker rebuild if local resources are constrained? Default: run it unless blocked and document the blocker.
- If real secrets are already present in local `.env`, should they be rotated by the user? Default: document the risk; do not rotate or print secrets.
