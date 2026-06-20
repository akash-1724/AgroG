# Testing and CI/CD Specification

## Purpose
Specifies automated test suites and continuous integration pipeline validation to verify repository stability.

## Requirements

### Requirement: Automated Backend Test Suite
The backend system SHALL provide an automated unit/integration test suite covering health checks, user authentication (registration, login, refresh, logout), RBAC guards (farmer/admin routes), marketplace listing CRUD permissions, cart checkout, order flow, stock checks, item-level fulfillment transitions, reviews/ratings, educational resources CRUD permissions, nearby farmer queries, recommendation history ownership, admin analytics access, listing image upload validation, and assistant safety mocks. During the final audit, backend tests SHALL be run or any failure SHALL be documented with cause and priority.

#### Scenario: Running the Backend Test Suite
- **WHEN** the backend test command is executed using pytest
- **THEN** the system SHALL run all test cases and return a clean success exit code (0) with test reports or document each failure in the final audit report

### Requirement: Automated ML Service Test Suite
The ML service SHALL provide a suite of automated unit tests covering input parameter range validation (pH, N, P, K, etc.), health and model status endpoints, disease detection format checks, and missing model fallback behaviours. During the final audit, ML service tests SHALL be run or any failure SHALL be documented with cause and priority.

#### Scenario: Running the ML Service Test Suite
- **WHEN** the ML service test command is run
- **THEN** the system SHALL run the validation assertions and verify demo fallbacks return expected metadata without crashing or document each failure in the final audit report

### Requirement: CI Pipeline Validation
The codebase SHALL feature a GitHub Actions workflow configuration (`.github/workflows/ci.yml`) triggered on pushes and pull requests to the main branch. The pipeline SHALL install dependencies, typecheck, lint, and run tests for the frontend, backend, and ML services. During the final audit, CI configuration SHALL be checked for current project structure and SHALL NOT require real external secrets for normal validation.

#### Scenario: Pull Request Triggered Validation
- **WHEN** a pull request is opened or updated targeting the main branch
- **THEN** GitHub Actions SHALL run the pipeline, checking types, linting, running tests, and reporting pass/fail status

#### Scenario: Final audit validates CI commands
- **WHEN** the final audit reviews CI/CD configuration
- **THEN** the CI commands SHALL match the current `frontend/`, `backend/`, and `ml_service/` project structure or the mismatch SHALL be documented as a finding

### Requirement: Final Verification Command List
The final audit SHALL run or document blockers for backend tests, ML tests, frontend lint, frontend typecheck, frontend build, Alembic upgrade, Docker Compose config, Docker stack startup, service health checks, OpenSpec active-change listing, and OpenSpec spec validation.

#### Scenario: Verification commands recorded
- **WHEN** the final audit report is produced
- **THEN** it SHALL list each required verification command with pass/fail/skipped status and any relevant limitation
