# Auth and RBAC Specification

## Purpose
Initial definition of the identity and authentication capability for AgroGuide.
## Requirements
### Requirement: User Registration and Profile Creation
The system SHALL allow users to register with an email, password, full name, phone number, and a role limited to farmer or customer for public registration. Farmer registration SHALL automatically initialize a corresponding empty FarmerProfile record in the database. Customer registration SHALL NOT require farmer fields. Public registration of Admin accounts is strictly prohibited and SHALL be verified during final audit.

#### Scenario: Successful Farmer Registration
- **WHEN** a user registers with valid farmer details, role, and password
- **THEN** the system SHALL create the user record, initialize a FarmerProfile mapping to their user ID, and return a success message

#### Scenario: Public admin registration blocked
- **WHEN** a public user attempts to register with role `admin`
- **THEN** the system SHALL reject the registration or downgrade it according to backend policy without creating a public admin account

### Requirement: JWT User Authentication
The system SHALL authenticate registered users using short-lived JWT access tokens and database-persisted, revocable refresh tokens. The system SHALL support access token regeneration via valid refresh tokens and revoke refresh tokens upon logout requests. The final audit SHALL verify registration, login, logout, refresh, refresh-token revocation, and `/me` behavior.

#### Scenario: Successful Email and Password Login
- **WHEN** a user logs in with correct email and password credentials
- **THEN** the system SHALL create a RefreshToken record in the database, return a short-lived JWT access token, and return a long-lived JWT refresh token

#### Scenario: Refresh token revocation verified
- **WHEN** a user logs out or reuses a revoked refresh token
- **THEN** the system SHALL prevent revoked refresh tokens from issuing new access tokens

### Requirement: Role-Based Access Control
The system SHALL enforce Role-Based Access Control (RBAC) on all protected API endpoints, restricting access to authorized roles (farmer, customer, admin). RBAC SHALL also enforce resource ownership for listing image management, order item fulfillment updates, customer carts/orders, reviews, recommendation history, admin analytics, and admin-managed resources. Final audit SHALL verify backend enforcement and SHALL NOT rely on frontend-only security assumptions.

#### Scenario: Farmer Accessing Marketplace Inventory
- **WHEN** an authenticated user with the role 'farmer' requests a farmer-only endpoint
- **THEN** the system SHALL authorize the request and return the resource data

#### Scenario: Admin accesses analytics
- **WHEN** an authenticated Admin requests admin analytics endpoints or opens the admin dashboard
- **THEN** the system SHALL authorize the request and return real analytics data

#### Scenario: Non-admin blocked from analytics
- **WHEN** a Farmer, Customer, or anonymous user requests admin analytics endpoints
- **THEN** the system SHALL reject the request with an authorization error

#### Scenario: Listing image ownership enforced
- **WHEN** a Farmer attempts to upload or delete images for a listing they do not own
- **THEN** the system SHALL reject the request with a forbidden or not-found response

#### Scenario: Order item ownership enforced
- **WHEN** a Farmer attempts to update fulfillment status for an order item tied to another Farmer's listing
- **THEN** the system SHALL reject the request with a forbidden or not-found response

#### Scenario: Admin ownership override
- **WHEN** an Admin manages listing images or order item statuses
- **THEN** the system SHALL allow the action regardless of listing ownership

#### Scenario: Final audit verifies ownership boundaries
- **WHEN** the final audit reviews protected backend endpoints
- **THEN** it SHALL verify or document ownership checks for farmer listings, customer carts/orders, farmer order items, reviews, recommendation history, admin analytics, and admin resources
