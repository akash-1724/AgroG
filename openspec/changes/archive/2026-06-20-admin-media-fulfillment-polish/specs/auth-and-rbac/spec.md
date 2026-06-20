## MODIFIED Requirements

### Requirement: Role-Based Access Control
The system SHALL enforce Role-Based Access Control (RBAC) on all protected API endpoints, restricting access to authorized roles (farmer, customer, admin). RBAC SHALL also enforce resource ownership for listing image management and order item fulfillment updates.

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
