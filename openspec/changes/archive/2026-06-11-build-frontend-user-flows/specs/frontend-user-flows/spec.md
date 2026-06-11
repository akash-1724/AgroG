## ADDED Requirements

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

### Requirement: Marketplace Browsing and Listing Details
The system SHALL provide a marketplace listing directory and a detailed page for specific listings, complete with search, filter, and sorting.

#### Scenario: Viewing listing directory
- **WHEN** a customer visits the `/marketplace` route
- **THEN** the marketplace displays active listings with options to search, filter by crop type, and sort by price or date

#### Scenario: Viewing listing details
- **WHEN** a user clicks on an active crop listing card
- **THEN** they are directed to `/marketplace/[id]` showing detailed information, pricing, quantities, farmer info, and an order creation section

---

### Requirement: Order Management
The system SHALL allow customers to place crop orders, view their own order history, and allow farmers to manage incoming orders.

#### Scenario: Placing an order
- **WHEN** a customer specifies a quantity on a crop listing detail page and submits an order
- **THEN** a pending order is created, a success message is displayed, and the customer is redirected to their orders list

#### Scenario: Farmer updating order status
- **WHEN** a farmer views an incoming order on `/farmer/orders` and updates the status (e.g., Confirmed, Shipped, Completed)
- **THEN** the updated status is sent to the backend, and the list updates to reflect the new state
