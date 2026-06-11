## MODIFIED Requirements

### Requirement: Marketplace Listing Creation
The system SHALL allow authenticated Farmers to create and update their own listings for agricultural crops, specifying title, description, price_per_unit, unit, available_quantity, category, status (`active`, `inactive`, `sold_out`), and photo/image URLs. Farmers SHALL NOT edit or update listings belonging to other farmers. Customers SHALL NOT update or write listing data.

#### Scenario: Creating a Crop Listing
- **WHEN** a Farmer submits a valid listing form with crop details
- **THEN** the system SHALL create the listing with the status defaulted to 'active'

#### Scenario: Unauthorized Edit Block
- **WHEN** a Farmer attempts to update a crop listing belonging to a different farmer
- **THEN** the system SHALL reject the request with a 403 Forbidden status

### Requirement: Customer Cart and Checkout
The system SHALL allow authenticated Customers to check out and place an order. At checkout, the system SHALL validate that the requested quantity is available in stock. The system SHALL deduct the ordered quantity from the listing's available stock transaction-safely and store a snapshot of the unit price in the `OrderItem` record. If the requested quantity exceeds stock, the checkout SHALL fail.

#### Scenario: Ordering Marketplace Items successfully
- **WHEN** a Customer checks out with a listing containing sufficient available stock
- **THEN** the system SHALL create the order, deduct stock from the listing, store the price snapshot, and mark the order status as pending

#### Scenario: Ordering Marketplace Items out of stock
- **WHEN** a Customer checks out requesting more quantity than is available in stock
- **THEN** the system SHALL reject the order creation and raise a 400 Bad Request error

### Requirement: Order Status Management
The system SHALL manage orders through a strict controlled status lifecycle: `pending` -> `accepted` -> `ready` -> `completed`, allowing rejection (`rejected`) or cancellation (`cancelled`). Stock SHALL be restored if a `pending` order is cancelled by the Customer or rejected/cancelled by a Farmer/Admin. Customers can only cancel their own `pending` orders. Farmers can only update status for orders containing their own listings. Admins can update any order.

#### Scenario: Customer Cancels Own Pending Order
- **WHEN** a Customer requests cancellation of their own pending order
- **THEN** the system SHALL update the status to 'cancelled', restore the listing's stock quantity, and return success

#### Scenario: Farmer Rejects Order
- **WHEN** a Farmer updates an order status containing their product to 'rejected'
- **THEN** the system SHALL update the status to 'rejected', restore the listing's stock quantity, and return success
