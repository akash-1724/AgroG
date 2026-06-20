## MODIFIED Requirements

### Requirement: Marketplace Browsing and Listing Details
The system SHALL provide a marketplace listing directory and a detailed page for specific listings, complete with search, filter, sorting, and uploaded listing image display.

#### Scenario: Viewing listing directory
- **WHEN** a customer visits the `/marketplace` route
- **THEN** the marketplace displays active listings with options to search, filter by crop type, sort by price or date, and view primary uploaded listing images when available

#### Scenario: Viewing listing details
- **WHEN** a user clicks on an active crop listing card
- **THEN** they are directed to `/marketplace/[id]` showing detailed information, uploaded listing images, pricing, quantities, farmer info, and an order creation section

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

## ADDED Requirements

### Requirement: Admin Dashboard Flow
The frontend SHALL provide an admin-only `/admin/dashboard` route that displays real database-backed analytics using cards and tables first.

#### Scenario: Admin views dashboard
- **WHEN** an authenticated Admin opens `/admin/dashboard`
- **THEN** the UI SHALL display analytics cards or tables for users, listings, orders, order value, advisory usage, resources, and reviews where data exists

#### Scenario: Non-admin blocked from dashboard
- **WHEN** a non-admin user attempts to open `/admin/dashboard`
- **THEN** the UI SHALL block access or redirect according to existing protected route behavior

### Requirement: Listing Image Upload Flow
The frontend SHALL provide image upload controls for listing create/edit flows and SHALL preview uploaded listing images.

#### Scenario: Farmer uploads listing image
- **WHEN** a Farmer selects a valid image file in the listing create/edit UI
- **THEN** the UI SHALL upload the file through the backend and show the uploaded image preview

#### Scenario: Listing image upload error shown
- **WHEN** image upload fails because of validation, ownership, or storage configuration
- **THEN** the UI SHALL show a clear error message without losing the listing form state
