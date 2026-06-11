## MODIFIED Requirements

### Requirement: User Registration and Profile Creation
The system SHALL allow users to register with an email, password, full name, phone number, and a role (farmer or customer). Farmer registration SHALL automatically initialize a corresponding empty FarmerProfile record in the database. Customer registration SHALL NOT require farmer fields. Public registration of Admin accounts is strictly prohibited.

#### Scenario: Successful Farmer Registration
- **WHEN** a user registers with valid farmer details, role, and password
- **THEN** the system SHALL create the user record, initialize a FarmerProfile mapping to their user ID, and return a success message

### Requirement: JWT User Authentication
The system SHALL authenticate registered users using short-lived JWT access tokens and database-persisted, revocable refresh tokens. The system SHALL support access token regeneration via valid refresh tokens and revoke refresh tokens upon logout requests.

#### Scenario: Successful Email and Password Login
- **WHEN** a user logs in with correct email and password credentials
- **THEN** the system SHALL create a RefreshToken record in the database, return a short-lived JWT access token, and return a long-lived JWT refresh token

### Requirement: Role-Based Access Control
The system SHALL enforce Role-Based Access Control (RBAC) on all protected API endpoints, restricting access to authorized roles (farmer, customer, admin).

#### Scenario: Farmer Accessing Marketplace Inventory
- **WHEN** an authenticated user with the role 'farmer' requests a farmer-only endpoint
- **THEN** the system SHALL authorize the request and return the resource data

## REMOVED Requirements

### Requirement: Google OAuth Authentication
**Reason**: Deferred to future phase to focus on stabilizing standard credentials.
**Migration**: Users must authenticate using standard email and password.
