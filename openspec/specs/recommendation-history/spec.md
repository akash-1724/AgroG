# Recommendation History Specification

## Purpose
Define authenticated recommendation history persistence, ownership, deletion, and frontend review flows.

## Requirements

### Requirement: Recommendation History Persistence
The system SHALL save authenticated users' crop, fertilizer, and disease recommendation requests and results as recommendation history records.

#### Scenario: Authenticated crop recommendation saved
- **WHEN** an authenticated user receives a crop recommendation
- **THEN** the system SHALL save a recommendation history record with type, input payload, result payload, model status, weather usage flag, user id, and created timestamp

#### Scenario: Authenticated fertilizer recommendation saved
- **WHEN** an authenticated user receives a fertilizer recommendation
- **THEN** the system SHALL save a recommendation history record with type, input payload, result payload, model status, user id, and created timestamp

#### Scenario: Authenticated disease recommendation saved
- **WHEN** an authenticated user receives a disease recommendation
- **THEN** the system SHALL save a recommendation history record with type, input payload, result payload, model status, user id, and created timestamp

### Requirement: Recommendation History Ownership
The system SHALL allow users to view and delete only their own recommendation history records.

#### Scenario: User lists own history
- **WHEN** an authenticated user requests recommendation history
- **THEN** the system SHALL return only records owned by that user

#### Scenario: Cross-user history access blocked
- **WHEN** an authenticated user requests a recommendation history record owned by another user
- **THEN** the system SHALL reject the request with a forbidden or not-found response

#### Scenario: User deletes own history item
- **WHEN** an authenticated user deletes one of their own recommendation history records
- **THEN** the system SHALL remove that record and return success

### Requirement: Recommendation History Frontend
The system SHALL provide frontend pages for authenticated users to list and inspect their saved recommendation history.

#### Scenario: User opens recommendation history list
- **WHEN** an authenticated user opens `/recommendations/history`
- **THEN** the UI SHALL show their saved recommendation records with type, date, model status, and weather-used indicator where applicable

#### Scenario: User opens recommendation history detail
- **WHEN** an authenticated user opens `/recommendations/history/{id}` for their own record
- **THEN** the UI SHALL show the saved input and result details for that recommendation
