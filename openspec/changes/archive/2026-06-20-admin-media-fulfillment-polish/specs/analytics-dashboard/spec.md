## MODIFIED Requirements

### Requirement: Business and Farming Metrics Dashboard
The system SHALL aggregate and present real database-backed operational analytics for Admin users, including users, listings, orders, order value, advisory/ML usage, disease detection usage, educational resources where available, and review/rating summaries where available. Analytics SHALL be admin-only and SHALL NOT be hardcoded or fabricated.

#### Scenario: Farmer Accesses Sales Dashboard
- **WHEN** an authenticated Farmer opens their dashboard
- **THEN** the system SHALL display their total sales, order statuses, and top-performing crop items

#### Scenario: Admin opens analytics dashboard
- **WHEN** an authenticated Admin opens `/admin/dashboard`
- **THEN** the frontend SHALL request admin analytics and display real aggregate cards or tables for users, listings, orders, order value, advisory usage, resources, and reviews where data exists

#### Scenario: Non-admin analytics access blocked
- **WHEN** a Farmer, Customer, or anonymous user requests admin analytics
- **THEN** the system SHALL reject the request with an authorization error

#### Scenario: Analytics use real data
- **WHEN** admin analytics are calculated
- **THEN** totals and breakdowns SHALL be computed from database tables and SHALL NOT use hardcoded fake analytics values

#### Scenario: Missing optional data handled
- **WHEN** optional tables such as reviews or educational resources have no records
- **THEN** analytics SHALL return zero or empty summaries without failing
