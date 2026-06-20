# Final Quality Audit Specification

## Purpose
Defines the final audit process used to verify AgroGuide quality, readiness, documentation, and OpenSpec consistency after feature implementation phases.

## Requirements
### Requirement: Final Audit Scope
The system SHALL have a final quality audit process that covers backend correctness, frontend correctness, ML service correctness, database/migrations, auth/RBAC, marketplace/cart/orders/fulfillment, farmer profiles/reviews/ratings, advisory ML/weather/price/history features, educational resources/location/assistant, admin analytics, image upload/Cloudinary integration, environment variables/secrets, Docker Compose, testing, CI/CD, documentation, deployment readiness, and OpenSpec consistency.

#### Scenario: Complete audit scope is recorded
- **WHEN** the final audit report is created
- **THEN** it SHALL include findings or explicit no-finding notes for every required audit area

#### Scenario: No product feature development
- **WHEN** the final audit is applied
- **THEN** it SHALL avoid adding new product features, paid services, payment gateway behavior, broad UI redesigns, repo structure changes, or new ML models

### Requirement: Finding Prioritization
The final audit SHALL classify findings as P0, P1, P2, or P3 using explicit severity rules.

#### Scenario: P0 finding classification
- **WHEN** a finding means the app cannot run, migrations cannot run, data can be lost, or a serious credential/security exposure exists
- **THEN** the finding SHALL be classified as P0

#### Scenario: P1 finding classification
- **WHEN** a finding breaks a core feature, auth/RBAC/ownership, checkout/order/review behavior, or backend/frontend API contract
- **THEN** the finding SHALL be classified as P1

#### Scenario: P2 finding classification
- **WHEN** a finding is an important test, CI, documentation, deployment, maintainability, or localized quality issue that does not break core flows
- **THEN** the finding SHALL be classified as P2

#### Scenario: P3 finding classification
- **WHEN** a finding is optional polish, cosmetic cleanup, or a future improvement
- **THEN** the finding SHALL be classified as P3

### Requirement: Apply Phase Fix Rules
The final audit apply phase SHALL fix P0 and P1 issues when feasible, fix only small safe localized P2 issues, and document large P2 or P3 issues instead of implementing them.

#### Scenario: Critical issue found
- **WHEN** a P0 or P1 issue is found during audit apply
- **THEN** the issue SHALL be fixed or explicitly documented as blocked with cause, risk, and recommended follow-up

#### Scenario: Large non-critical issue found
- **WHEN** a large P2 or any P3 issue is found during audit apply
- **THEN** the issue SHALL be documented in the final audit report rather than implemented automatically

### Requirement: Final Audit Report
The final audit SHALL produce `docs/final-quality-audit.md` containing the scope, initial worktree/OpenSpec state, prioritization rules, findings by priority, fixes applied, blocked/deferred items, verification results, environment/secrets review, deployment readiness notes, OpenSpec consistency status, known limitations, and final assessment.

#### Scenario: Final report created
- **WHEN** the audit apply phase completes
- **THEN** `docs/final-quality-audit.md` SHALL exist and summarize the exact verification results and remaining risks

#### Scenario: Worktree state recorded
- **WHEN** the audit apply phase starts
- **THEN** the final audit report SHALL record a summarized initial git status and diff stat so audit-created changes can be distinguished from pre-existing work

#### Scenario: Verification failure documented
- **WHEN** a required verification command fails and cannot be fixed within scope
- **THEN** the final audit report SHALL include the failing command, failure cause, priority, and follow-up recommendation

### Requirement: Final Readiness Acceptance
The audit SHALL require backend startup, frontend build, ML service startup, migrations, Docker Compose validation, backend tests, frontend checks, ML tests, safe environment documentation, README/setup accuracy, and clean OpenSpec status to pass or be documented with cause.

#### Scenario: Ready final assessment
- **WHEN** all required checks pass or allowed limitations are documented
- **THEN** the final audit report SHALL state that the project is ready for review with known limitations listed

#### Scenario: Blocked final assessment
- **WHEN** P0 or P1 issues remain unresolved
- **THEN** the final audit report SHALL state that the project is not ready and list blockers first

### Requirement: Worktree Safety
The final audit SHALL preserve unrelated existing worktree changes and SHALL NOT revert or overwrite user changes that are outside the audited fix scope.

#### Scenario: Existing unrelated changes present
- **WHEN** the audit finds pre-existing modified or untracked files
- **THEN** the audit SHALL record them at a summary level and avoid reverting or overwriting unrelated changes

#### Scenario: Fix overlaps changed file
- **WHEN** an allowed audit fix must touch a file that already contains unrelated changes
- **THEN** the fix SHALL be minimal and compatible with the existing file state, or the blocker SHALL be documented
