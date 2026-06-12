## ADDED Requirements

### Requirement: Automated Backend Test Suite
The backend system SHALL provide an automated unit/integration test suite covering health checks, user authentication (registration, login, refresh, logout), RBAC guards (farmer/admin routes), marketplace listing CRUD permissions, order flow (creation, stock checks, status transitions), educational resources CRUD permissions, nearby farmer queries, and assistant safety mocks.

#### Scenario: Running the Backend Test Suite
- **WHEN** the backend test command is executed using pytest
- **THEN** the system SHALL run all test cases and return a clean success exit code (0) with test reports

### Requirement: Automated ML Service Test Suite
The ML service SHALL provide a suite of automated unit tests covering input parameters range validation (pH, N, P, K, etc.), health and model status endpoints, disease detection format checks, and missing model fallback behaviours.

#### Scenario: Running the ML Service Test Suite
- **WHEN** the ML service test command is run
- **THEN** the system SHALL run the validation assertions and verify demo fallbacks return expected metadata without crashing

### Requirement: CI Pipeline Validation
The codebase SHALL feature a GitHub Actions workflow configuration (`.github/workflows/ci.yml`) triggered on pushes and pull requests to the main branch. The pipeline SHALL install dependencies, typecheck, lint, and run tests for the frontend, backend, and ML services.

#### Scenario: Pull Request Triggered Validation
- **WHEN** a pull request is opened or updated targeting the main branch
- **THEN** GitHub Actions SHALL run the pipeline, checking types, linting, running tests, and reporting pass/fail status
