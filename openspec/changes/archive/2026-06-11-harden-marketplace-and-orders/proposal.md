## Why

The current marketplace and order implementation is a basic scaffold. To transition it into a robust, secure, and production-style core, we need to enforce strict data ownership rules (RBAC/ownership checks), manage listing lifecycle status safely, prevent race conditions during checkout via transaction-safe inventory validation, enforce controlled state transitions for orders, and enable clean listing search, filtering, and pagination.

## What Changes

- **CropListing Status & Metadata**:
  - Add explicit listing status (`active`, `inactive`, `sold_out`) and category support (`category` string or enumeration) to `CropListing`.
- **Safe Inventory & Price Snapshots**:
  - Verify and enforce database-level stock deduction at the time of checkout.
  - Implement stock restoration if orders are cancelled or rejected.
  - Store the purchase-time price snapshot in `OrderItem` to protect against subsequent listing updates.
- **Controlled Order Status Lifecycle**:
  - Enforce status transitions: `pending` -> `accepted` -> `ready` -> `completed`, and allow `rejected` or `cancelled`.
  - Block invalid state transitions (e.g. going from `completed` back to `pending`).
- **Strict Role-Based and Ownership Authorization**:
  - **Farmers**: Can manage only their own listings and view/update statuses of orders that contain their products.
  - **Customers**: Can view active listings, place orders, view their own order history, and cancel only their own `pending` orders.
  - **Admins**: Full global access to manage any listing or order.
- **Search, Filter, and Pagination**:
  - Enable case-insensitive search (name/description), filtering by category and status, sorting (price high-low/low-high, latest), and standard limit/offset pagination.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `farmer-marketplace`: Enforce strict listing lifecycle management, safe stock validation/restoration, price snapshotting, ownership checks for farmers/customers/admins, controlled order lifecycle transitions, and API search/filtering/pagination query handlers.

## Impact

- **Database**: Add status and category columns to `crop_listings`. A new database migration script will be needed.
- **Backend APIs**:
  - Modify `/api/v1/marketplace/listings` to support paginated search, filter, and sort query parameters.
  - Apply strict dependencies (`RoleChecker` and ownership checks) on listing edits/deletes.
  - Modify `/api/v1/marketplace/orders` to lock down stock validation, transactional updates, and conditional status changes.
- **Testing**: Requires automated verification tests (`verify_marketplace.py`) simulating concurrent ordering, status manipulation, and privilege-escalation attempts.
