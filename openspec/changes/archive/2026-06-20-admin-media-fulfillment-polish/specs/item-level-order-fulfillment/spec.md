## ADDED Requirements

### Requirement: Order Item Fulfillment Status
The system SHALL track fulfillment status on each order item using the lifecycle `pending`, `accepted`, `rejected`, `ready`, `completed`, and `cancelled`.

#### Scenario: Checkout creates pending order items
- **WHEN** a Customer checks out one or more cart items
- **THEN** each created order item SHALL start with status `pending`

#### Scenario: Item status timestamp updated
- **WHEN** an order item status changes
- **THEN** the system SHALL update a status timestamp and, when completed, a fulfilled timestamp where available

### Requirement: Farmer Order Item Status Updates
The system SHALL allow Farmers to update only order items tied to listings they own.

#### Scenario: Farmer updates own item
- **WHEN** a Farmer updates the status of an order item for their own listing
- **THEN** the system SHALL apply the valid status transition and return the updated item

#### Scenario: Farmer cannot update another farmer's item
- **WHEN** a Farmer attempts to update an order item tied to another Farmer's listing
- **THEN** the system SHALL reject the request with a forbidden or not-found response

### Requirement: Customer Item Status Visibility
The system SHALL show Customers item-level fulfillment statuses for their own orders.

#### Scenario: Customer views order detail
- **WHEN** a Customer views one of their orders
- **THEN** the response and UI SHALL show each order item's fulfillment status and the aggregate order status

### Requirement: Aggregate Order Status Derivation
The system SHALL derive the aggregate order status from item-level statuses so multi-farmer orders remain consistent.

#### Scenario: Mixed item statuses
- **WHEN** an order contains items in different fulfillment statuses
- **THEN** the aggregate order status SHALL reflect the combined item state without hiding individual item statuses

#### Scenario: All items completed
- **WHEN** all order items are completed
- **THEN** the aggregate order status SHALL become `completed`

#### Scenario: All items rejected or cancelled
- **WHEN** all order items are terminally rejected or cancelled
- **THEN** the aggregate order status SHALL become `cancelled` or `rejected` according to backend derivation rules

### Requirement: Stock Restoration for Item Rejection or Cancellation
The system SHALL restore listing stock for rejected or cancelled order items when stock had previously been deducted and SHALL avoid double restoration.

#### Scenario: Farmer rejects pending item
- **WHEN** a Farmer rejects a pending order item for their listing
- **THEN** the system SHALL restore that item's ordered quantity to the listing stock once and mark the item rejected

#### Scenario: Repeated terminal update does not double restore
- **WHEN** an already rejected or cancelled order item receives another terminal update request
- **THEN** the system SHALL NOT restore stock a second time

### Requirement: Admin Order Item Management
The system SHALL allow Admin users to view and update any order item's fulfillment status.

#### Scenario: Admin updates any item
- **WHEN** an Admin updates an order item status
- **THEN** the system SHALL apply the valid update regardless of listing ownership

### Requirement: Farmer Order Item Frontend
The frontend SHALL show Farmers only their relevant order items and provide valid item status actions.

#### Scenario: Farmer views order items
- **WHEN** a Farmer opens `/farmer/orders`
- **THEN** the UI SHALL show only order items for that Farmer's listings with item-level status controls

#### Scenario: Customer sees item statuses
- **WHEN** a Customer opens their orders page or order detail
- **THEN** the UI SHALL show item-level fulfillment statuses for each item
