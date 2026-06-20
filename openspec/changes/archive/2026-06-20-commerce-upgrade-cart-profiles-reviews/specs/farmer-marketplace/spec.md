## MODIFIED Requirements

### Requirement: Customer Cart and Checkout
The system SHALL require authenticated Customers to use the cart flow before marketplace checkout. Customers SHALL add listing items to cart from listing cards or listing detail pages, review cart contents on `/cart`, and submit checkout from the cart page. At checkout, the system SHALL validate that every requested listing is active and has sufficient available stock. The system SHALL deduct ordered quantity from listing stock transaction-safely, store a snapshot of unit price in each `OrderItem`, create order records according to the existing backend order design, and clear the cart after successful checkout. If any requested quantity exceeds stock, checkout SHALL fail without creating an order.

#### Scenario: Ordering Marketplace Items successfully
- **WHEN** a Customer checks out a cart containing listings with sufficient available stock
- **THEN** the system SHALL create the order, deduct stock from each listing, store price snapshots, clear the cart, and mark the order status as pending

#### Scenario: Ordering Marketplace Items out of stock
- **WHEN** a Customer checks out a cart requesting more quantity than is available for any listing
- **THEN** the system SHALL reject checkout and raise a 400 Bad Request error without creating an order

#### Scenario: Direct listing checkout blocked
- **WHEN** a Customer attempts to place an order directly from a listing detail page without using the cart flow
- **THEN** the frontend SHALL route the Customer through add-to-cart and `/cart` checkout instead of direct order placement

## ADDED Requirements

### Requirement: Marketplace Listing Rating Display
The marketplace SHALL show derived listing and farmer rating summaries on listing cards and listing detail pages when review data exists. Rating summaries SHALL include average rating and review count.

#### Scenario: Listing card shows rating summary
- **WHEN** a listing has one or more reviews
- **THEN** the listing card SHALL display the average rating and review count

#### Scenario: Listing detail shows review state
- **WHEN** a listing has no reviews
- **THEN** the listing detail page SHALL show an unrated or zero-review state without fabricating a rating
