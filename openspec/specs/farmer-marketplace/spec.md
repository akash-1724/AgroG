# Farmer Marketplace Specification

## Purpose
Initial definition of the Farmer Marketplace capability for AgroGuide.

## Requirements

### Requirement: Marketplace Listing Creation
The system SHALL allow authenticated Farmers to create listings for agricultural crops, specifying title, description, price, quantity, unit, and photos.

#### Scenario: Creating a Crop Listing
- **WHEN** a Farmer submits a valid listing form with crop details
- **THEN** the system SHALL create the listing, upload photos to Cloudinary, and set the status to active

### Requirement: Customer Cart and Checkout
The system SHALL allow authenticated Customers to add crop listings to a cart and check out to place an order.

#### Scenario: Ordering Marketplace Items
- **WHEN** a Customer checks out a cart containing available crop listings
- **THEN** the system SHALL create an order, reserve the inventory quantity, and mark the order status as pending

### Requirement: Order Status Management
The system SHALL allow Farmers to update order statuses (e.g., pending, shipped, completed, cancelled) and allow Customers to view updates.

#### Scenario: Farmer Ships an Order
- **WHEN** a Farmer updates an order status to 'shipped'
- **THEN** the system SHALL update the order status in the database and notify the Customer
