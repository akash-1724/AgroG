## Why

AgroGuide needs automated test suites, CI/CD pipeline verification, and a comprehensive deployment architecture to ensure the platform is verifiable, stable, and ready to be deployed on free/practical hosting tiers.

## What Changes

- Add backend test suites covering health, auth, RBAC, orders, listings, location, and assistant.
- Add ML service test suites verifying range validation, health, fallback behaviors, and image upload limits.
- Set up GitHub Actions CI (`.github/workflows/ci.yml`) to automatically install dependencies, typecheck, lint, and run tests for frontend, backend, and ML service.
- Create deployment planning, environment checklists, production readiness checklists, and verification guides.

## Capabilities

### New Capabilities
- `testing`: Defines requirements for automated test suites, CI workflow checks, and manual frontend validation flows.

### Modified Capabilities
None.

## Impact

- **CI/CD**: Adds GitHub Actions CI configuration.
- **Testing**: Adds backend and ML service test scripts.
- **Documentation**: Creates production deployment plans, testing guides, and environment setups.
