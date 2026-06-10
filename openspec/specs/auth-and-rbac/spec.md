# Auth and RBAC Specification

## Purpose
Initial definition of the identity and authentication capability for AgroGuide.

## Requirements

### Requirement: User Registration and Profile Creation
The system SHALL allow users to register with an email, password, full name, phone number, and a role (Farmer, Customer, or Admin).

#### Scenario: Successful Farmer Registration
- **WHEN** a user registers with valid Farmer details and password
- **THEN** the system SHALL create the user record, default their status to active, and return a success message

### Requirement: JWT User Authentication
The system SHALL authenticate registered users using JWT access and refresh tokens.

#### Scenario: Successful Email and Password Login
- **WHEN** a user logs in with correct email and password credentials
- **THEN** the system SHALL return a short-lived JWT access token and a long-lived JWT refresh token

### Requirement: Google OAuth Authentication
The system SHALL support Google OAuth 2.0 login and register users automatically if their email does not already exist.

#### Scenario: Login with Valid Google Account
- **WHEN** a user successfully authenticates via Google OAuth
- **THEN** the system SHALL return JWT access and refresh tokens associated with that email

### Requirement: Role-Based Access Control
The system SHALL enforce Role-Based Access Control (RBAC) on all protected API endpoints and frontend routes.

#### Scenario: Farmer Accessing Marketplace Inventory
- **WHEN** an authenticated user with the role 'Farmer' requests a Farmer-only endpoint
- **THEN** the system SHALL authorize the request and return the resource data
