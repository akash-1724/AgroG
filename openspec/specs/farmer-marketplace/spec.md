# Farmer Marketplace Specification

## Purpose
Initial definition of the Farmer Marketplace capability for AgroGuide.
## Requirements
### Requirement: Marketplace Listing Creation
The system SHALL allow authenticated Farmers to create and update their own listings for agricultural crops, specifying title, description, price_per_unit, unit, available_quantity, category, and status (`active`, `inactive`, `sold_out`). The system SHALL support backend-managed uploaded listing images instead of requiring pasted image URLs. Farmers SHALL NOT edit or update listings belonging to other farmers. Customers SHALL NOT update or write listing data.

#### Scenario: Creating a Crop Listing
- **WHEN** a Farmer submits a valid listing form with crop details
- **THEN** the system SHALL create the listing with the status defaulted to 'active'

#### Scenario: Unauthorized Edit Block
- **WHEN** a Farmer attempts to update a crop listing belonging to a different farmer
- **THEN** the system SHALL reject the request with a 403 Forbidden status

#### Scenario: Listing includes uploaded images
- **WHEN** a Farmer uploads images for their listing
- **THEN** listing responses SHALL include the uploaded image metadata and displayable image URLs

### Requirement: Customer Cart and Checkout
The system SHALL require authenticated Customers to use the cart flow before marketplace checkout. Customers SHALL add listing items to cart from listing cards or listing detail pages, review cart contents on `/cart`, and submit checkout from the cart page. At checkout, the system SHALL validate that every requested listing is active and has sufficient available stock. The system SHALL deduct ordered quantity from listing stock transaction-safely, store a snapshot of unit price in each `OrderItem`, create order records according to the existing backend order design, clear the cart after successful checkout, and initialize created order items with item-level fulfillment status `pending`. If any requested quantity exceeds stock, checkout SHALL fail without creating an order.

#### Scenario: Ordering Marketplace Items successfully
- **WHEN** a Customer checks out a cart containing listings with sufficient available stock
- **THEN** the system SHALL create the order, deduct stock from each listing, store price snapshots, clear the cart, mark the order status as pending, and mark each order item as pending

#### Scenario: Ordering Marketplace Items out of stock
- **WHEN** a Customer checks out a cart requesting more quantity than is available for any listing
- **THEN** the system SHALL reject checkout and raise a 400 Bad Request error without creating an order

#### Scenario: Direct listing checkout blocked
- **WHEN** a Customer attempts to place an order directly from a listing detail page without using the cart flow
- **THEN** the frontend SHALL route the Customer through add-to-cart and `/cart` checkout instead of direct order placement

### Requirement: Order Status Management
The system SHALL manage marketplace fulfillment through item-level order statuses using the lifecycle `pending`, `accepted`, `rejected`, `ready`, `completed`, and `cancelled`. The aggregate order status SHALL be derived from item statuses. Stock SHALL be restored when a pending or active order item is rejected or cancelled and SHALL NOT be restored twice. Customers can view their item statuses and cancel eligible own pending items or orders where supported. Farmers can only update statuses for order items containing their own listings. Admins can update any order item.

#### Scenario: Customer Cancels Own Pending Order
- **WHEN** a Customer requests cancellation of their own pending order or eligible pending order items
- **THEN** the system SHALL update the relevant item statuses to 'cancelled', restore listing stock quantity once, derive the aggregate order status, and return success

#### Scenario: Farmer Rejects Order
- **WHEN** a Farmer updates one of their own order item statuses to 'rejected'
- **THEN** the system SHALL update the item status to 'rejected', restore that item's listing stock quantity once, derive the aggregate order status, and return success

#### Scenario: Farmer updates only own order item
- **WHEN** a Farmer attempts to update an order item tied to another Farmer's listing
- **THEN** the system SHALL reject the update with a forbidden or not-found response

#### Scenario: Customer views item-level fulfillment
- **WHEN** a Customer views an order containing items from multiple farmers
- **THEN** the system SHALL show each order item's status and the aggregate order status

### Requirement: Marketplace Listing Rating Display
The marketplace SHALL show derived listing and farmer rating summaries on listing cards and listing detail pages when review data exists. Rating summaries SHALL include average rating and review count.

#### Scenario: Listing card shows rating summary
- **WHEN** a listing has one or more reviews
- **THEN** the listing card SHALL display the average rating and review count

#### Scenario: Listing detail shows review state
- **WHEN** a listing has no reviews
- **THEN** the listing detail page SHALL show an unrated or zero-review state without fabricating a rating
