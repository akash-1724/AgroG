## Context

The existing database structures `CropListing`, `Order`, and `OrderItem` are basic scaffolds lacking status/category attributes, data ownership control layers, transaction-safe inventory checks, and price snapshotting features. This design plans the hardening of the database, security dependencies, and HTTP routers.

## Goals / Non-Goals

**Goals:**
- Add `status` and `category` fields to `CropListing` models.
- Support full paginated search, filtering, and sorting parameters on `/api/v1/marketplace/listings`.
- Enforce that farmers can edit/delete/deactivate only their own crop listings.
- Enforce transactional stock deduction at checkout, blocking checkout if stock is insufficient.
- Store purchase-time price in `OrderItem` as a snapshot.
- Implement strict status transition controls: `pending` -> `accepted` -> `ready` -> `completed`, allowing rejection or cancellation.
- Restore listing stock when orders are rejected or cancelled.
- Ensure strict ownership checks on orders: Customers view only their own orders; Farmers view only orders containing their own listings; Admins view all.

**Non-Goals:**
- Defer Google OAuth integration.
- Defer external payments integrations.
- Defer Cloudinary/external file hosting configurations.
- Defer machine learning and frontend dashboards.

## Decisions

### 1. Database Schema Updates
- **Decision**: Add `status` (String, default="active") and `category` (String, default="Vegetables") to `CropListing`. Use Alembic migrations.
- **Alternatives**: Create a distinct `Category` table. Declined to keep the schema simple and avoid complex table joins.

### 2. Transactional Checkout & Stock Checks
- **Decision**: Perform order placement inside a database transaction block (`db.begin()`). Select crop listings with `with_for_update()` to prevent race conditions. Deduct stock immediately.
- **Alternatives**: Let database triggers handle stock deduction, or validate stock asynchronously. Declined due to increased complexity and lack of immediate error feedback to the customer.

### 3. Price Snapshotting
- **Decision**: Save the `price_per_unit` of `CropListing` into `OrderItem.price_at_purchase` at the moment of checkout.
- **Alternatives**: Dynamically lookup prices during billing. Declined because subsequent price updates by a farmer would alter historical invoices.

### 4. RBAC & Data Ownership Security
- **Decision**: Define a custom FastAPI dependency or validation handler checking user role and resource ownership.
  - Farmers can update only listings where `listing.farmer_id == current_user.id` (or `farmer_profile.user_id`).
  - Farmers can view/update order status if any of the items in the order belong to their listings.
  - Customers can view orders where `order.customer_id == current_user.id`.
  - Admins override all checks.

### 5. Order Status Transition Matrix
- **Decision**: Implement a state machine validator function blocking invalid status transitions:
  - Allowed status values: `pending`, `accepted`, `rejected`, `ready`, `completed`, `cancelled`.
  - From `pending`: can transition to `accepted`, `rejected`, or `cancelled`.
  - From `accepted`: can transition to `ready` or `cancelled`.
  - From `ready`: can transition to `completed` or `cancelled`.
  - Terminal states (`completed`, `rejected`, `cancelled`) cannot transition to any other status.
  - If transitioning *to* `cancelled` or `rejected` from a state that deducted stock, restore the stock to the listing.

## Risks / Trade-offs

- **[Risk] Multiple Farmers in a Single Order** -> If a customer orders products from different farmers, a status update by one farmer affects the whole order.
  - *Mitigation*: Limit order statuses to be updated by farmers per-item or split orders into distinct vendor sub-orders if necessary. For this phase, we will check that if a farmer updates an order status, it contains at least one of their items, and they only modify status details relevant to their scope, or we enforce status updates globally on the order level while validating they own at least one item.
