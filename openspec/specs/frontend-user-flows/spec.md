# frontend-user-flows Specification

## Purpose
TBD - created by archiving change build-frontend-user-flows. Update Purpose after archive.
## Requirements
### Requirement: User Authentication Flow
The system SHALL support user login, logout, and session restoration using standard email and password authentication.

#### Scenario: Successful login
- **WHEN** a user enters valid email and password credentials and clicks login
- **THEN** the API returns a JWT token, client-side session state is populated, and the user is redirected to the dashboard or marketplace

#### Scenario: Failed login
- **WHEN** a user enters incorrect credentials or an invalid email format
- **THEN** client validation or backend errors are displayed on the form, and the user remains on the login page

#### Scenario: User registration with role selection
- **WHEN** a customer registers with name, email, password, or a farmer registers with additional farm name/profile fields
- **THEN** the user is created on the backend and immediately authenticated or redirected to login

#### Scenario: Protected route redirection
- **WHEN** an unauthenticated visitor attempts to access protected routes (e.g., `/orders`, `/farmer/listings`)
- **THEN** they are redirected to the `/login` route

---

### Requirement: Advisory Navigation
The frontend SHALL provide navigation paths for advisory features including crop recommendations, fertilizer recommendations, disease detection, price trends, and recommendation history where appropriate for the authenticated user.

#### Scenario: User sees price trend entry point
- **WHEN** a user views primary navigation or advisory landing content
- **THEN** the UI SHALL provide an entry point to `/prices`

#### Scenario: Authenticated user sees recommendation history entry point
- **WHEN** an authenticated user views advisory navigation or recommendation pages
- **THEN** the UI SHALL provide an entry point to `/recommendations/history`

#### Scenario: Weather disclosure visible in crop recommendation flow
- **WHEN** a user receives a weather-aware crop recommendation
- **THEN** the UI SHALL show whether weather data was used or unavailable

---

### Requirement: Marketplace Browsing and Listing Details
The system SHALL provide a marketplace listing directory and a detailed page for specific listings, complete with search, filter, sorting, and uploaded listing image display.

#### Scenario: Viewing listing directory
- **WHEN** a customer visits the `/marketplace` route
- **THEN** the marketplace displays active listings with options to search, filter by crop type, sort by price or date, and view primary uploaded listing images when available

#### Scenario: Viewing listing details
- **WHEN** a user clicks on an active crop listing card
- **THEN** they are directed to `/marketplace/[id]` showing detailed information, uploaded listing images, pricing, quantities, farmer info, and an order creation section

---

### Requirement: Order Management
The system SHALL allow customers to place crop orders, view their own order history with item-level fulfillment statuses, and allow farmers to manage incoming order items for their own listings.

#### Scenario: Placing an order
- **WHEN** a customer specifies a quantity on a crop listing detail page and submits an order
- **THEN** a pending order is created, item-level fulfillment statuses are initialized, a success message is displayed, and the customer is redirected to their orders list

#### Scenario: Farmer updating order status
- **WHEN** a farmer views an incoming order item on `/farmer/orders` and updates the item status
- **THEN** the updated item status is sent to the backend, and the list updates to reflect the new item-level state

#### Scenario: Customer views item-level statuses
- **WHEN** a customer opens their orders page or order detail
- **THEN** the UI SHALL show aggregate order status and individual order item statuses

---

### Requirement: Admin Dashboard Flow
The frontend SHALL provide an admin-only `/admin/dashboard` route that displays real database-backed analytics using cards and tables first.

#### Scenario: Admin views dashboard
- **WHEN** an authenticated Admin opens `/admin/dashboard`
- **THEN** the UI SHALL display analytics cards or tables for users, listings, orders, order value, advisory usage, resources, and reviews where data exists

#### Scenario: Non-admin blocked from dashboard
- **WHEN** a non-admin user attempts to open `/admin/dashboard`
- **THEN** the UI SHALL block access or redirect according to existing protected route behavior

---

### Requirement: Listing Image Upload Flow
The frontend SHALL provide image upload controls for listing create/edit flows and SHALL preview uploaded listing images.

#### Scenario: Farmer uploads listing image
- **WHEN** a Farmer selects a valid image file in the listing create/edit UI
- **THEN** the UI SHALL upload the file through the backend and show the uploaded image preview

#### Scenario: Listing image upload error shown
- **WHEN** image upload fails because of validation, ownership, or storage configuration
- **THEN** the UI SHALL show a clear error message without losing the listing form state
