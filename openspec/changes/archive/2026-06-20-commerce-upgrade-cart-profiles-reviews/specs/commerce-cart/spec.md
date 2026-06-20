## ADDED Requirements

### Requirement: Customer Cart Management
The system SHALL provide an authenticated customer cart that stores listing items before checkout. Customers SHALL be able to add active listing items, update quantities, remove items, clear the cart, and view item names, farmer names, unit prices, quantities, subtotals, and estimated total.

#### Scenario: Add listing to cart
- **WHEN** an authenticated Customer adds an active listing with a positive quantity
- **THEN** the system SHALL create or update that Customer's cart item for the listing and return the updated cart summary

#### Scenario: Update cart quantity
- **WHEN** an authenticated Customer updates one of their cart item quantities to a positive value
- **THEN** the system SHALL persist the new quantity and recalculate subtotals and estimated total

#### Scenario: Remove cart item
- **WHEN** an authenticated Customer removes one of their cart items
- **THEN** the system SHALL delete that item from the cart and return success

#### Scenario: Clear cart
- **WHEN** an authenticated Customer clears their cart
- **THEN** the system SHALL remove all items from that Customer's cart

### Requirement: Cart Ownership Enforcement
The system SHALL enforce that cart and cart item operations are scoped to the authenticated Customer who owns the cart. Farmers, Admins acting as regular commerce users, anonymous users, and other Customers SHALL NOT modify a Customer's cart items.

#### Scenario: Cross-customer cart item access blocked
- **WHEN** a Customer attempts to update or delete a cart item belonging to another Customer
- **THEN** the system SHALL reject the request with a forbidden or not-found response

#### Scenario: Anonymous cart API access blocked
- **WHEN** an anonymous user calls an authenticated cart endpoint
- **THEN** the system SHALL reject the request as unauthorized

### Requirement: Cart Stock Validation
The system SHALL validate listing status and available stock when items are added, updated, and checked out. Checkout SHALL fail if any cart item references an inactive, sold-out, deleted, or under-stocked listing.

#### Scenario: Add quantity beyond stock blocked
- **WHEN** a Customer attempts to add or update a cart item quantity above the listing's available stock
- **THEN** the system SHALL reject the request and explain the stock limitation

#### Scenario: Checkout stale cart blocked
- **WHEN** a Customer checks out a cart after one listing becomes inactive or under-stocked
- **THEN** the system SHALL reject checkout without creating an order and identify the invalid item

### Requirement: Cart Checkout Creates Orders
The system SHALL convert valid cart items into existing marketplace order and order item records using current listing prices as purchase snapshots. Successful checkout SHALL deduct stock transaction-safely and clear the Customer's cart.

#### Scenario: Successful cart checkout
- **WHEN** a Customer checks out a cart where all items are active and sufficiently stocked
- **THEN** the system SHALL create an order with order items, deduct stock, store price snapshots, mark the order pending, clear the cart, and return the created order

#### Scenario: Empty cart checkout blocked
- **WHEN** a Customer attempts checkout with an empty cart
- **THEN** the system SHALL reject the request without creating an order
