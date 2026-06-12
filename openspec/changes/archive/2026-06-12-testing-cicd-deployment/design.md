## Context

AgroGuide needs to ensure production stability, code verification, CI/CD pipeline automation, and a clear guide to deploy on free/hobby hosting tiers.

## Goals / Non-Goals

**Goals:**
- Implement backend automated test scripts verifying health, auth, RBAC, marketplace, orders, locations, assistant, and resources.
- Implement ML service automated test scripts verifying range checks, disease file upload size validation, and demo mode fallback metadata.
- Set up a GitHub Actions configuration `.github/workflows/ci.yml` running typechecks, lints, and test checks on every PR or push.
- Author clear production deployment plans and checklists.

**Non-Goals:**
- Deploying the app live automatically to paid services or performing infrastructure purchasing.
- Adding new business product features.

## Decisions

### 1. GitHub Actions CI Architecture

We will create a `.github/workflows/ci.yml` configuration:
- Runs on Ubuntu runner.
- Environment variables use dummy mock placeholders.
- Consists of three parallel jobs:
  1. `backend-ci`: Installs python, installs `requirements.txt`, runs `pytest`.
  2. `frontend-ci`: Installs node, runs `npm install`, runs `npm run build` (which triggers typechecks and linting checkups).
  3. `ml-service-ci`: Installs python, installs `ml_service/requirements.txt` if available, and runs tests.

### 2. Backend Test Strategy

We will introduce a test suite using `pytest` and `httpx.AsyncClient` targeting the FastAPI backend.
- We will mock the database session using a temporary SQLite memory database or test SQLite file (`test_agroguide.db`) to ensure tests do not require a running PostgreSQL instance in CI.
- Authentication checks will test register -> login -> profile query -> refresh token -> logout sequences.
- RBAC tests will verify role restrictions (e.g. `RoleChecker(["farmer"])` rejects customer users).

### 3. ML Service Test Strategy

We will write unit tests using `pytest` for the `ml_service`:
- Assert pH ranges strictly trigger Pydantic validation errors when $< 3.5$ or $> 9.0$.
- Assert crop/fertilizer inputs validate ranges correctly.
- Verify image size restrictions reject files $> 5\text{MB}$.

### 4. Free Deployment Architecture

- **Frontend**: Vercel (Free Hobby tier, linked to git repo, auto-deploys main pushes).
- **Backend API**: Render (Free Web Service) or Railway (Free trial tier).
- **Database**: Supabase (Free tier PostgreSQL) or Neon.tech (Serverless free PostgreSQL).
- **Redis**: Upstash (Free serverless Redis, compatible with redis client).
- **ML Service**: Render (deployed as a separate free web service) or unified within backend if resources are constrained.

## Risks / Trade-offs

- **Risk** -> Render free tier databases spin down after inactivity, causing initial API requests to lag.
  - **Mitigation** -> Implement frontend loading spinners and clean error messages to handle API wake-up delay.
- **Risk** -> CI runs out of memory or runs slowly building Next.js.
  - **Mitigation** -> Leverage cached `node_modules` actions to accelerate build steps.
