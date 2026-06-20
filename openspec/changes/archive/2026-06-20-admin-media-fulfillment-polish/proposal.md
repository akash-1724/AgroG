## Why

AgroGuide now has marketplace, advisory intelligence, reviews, carts, and recommendation history, but the final product still lacks admin visibility, real listing media upload, and clear fulfillment handling for multi-farmer cart orders. This change adds production-style polish while keeping the project small, free-tier friendly, and honest about scope.

## What Changes

- Add an admin-only analytics dashboard backed by real database aggregates for users, listings, orders, order value, advisory/ML usage, resources, and reviews where data exists.
- Add backend admin analytics endpoints, starting with `GET /api/v1/admin/analytics/overview`, with optional detailed order and ML usage endpoints if they stay small.
- Replace pasted listing image URL workflows with backend-mediated image upload storage.
- Use Cloudinary only when `CLOUDINARY_URL` is configured; do not expose Cloudinary secrets to the frontend.
- Add controlled media upload errors or a local development fallback if a simple existing-safe pattern is available.
- Add listing image ownership rules so only listing-owner farmers or admins can manage listing images.
- Add validated file upload constraints for image MIME type, extension, and size.
- Support multiple listing images where feasible through a dedicated `ListingImage`/`ProductImage` table or a minimal equivalent schema.
- Add item-level order fulfillment for multi-farmer orders using `OrderItem` statuses rather than a single coarse order status.
- Add farmer-only item status updates scoped to that farmer's own listing items, customer-visible item statuses, admin override capability, aggregate order status derivation, and stock restoration rules.
- Update frontend admin, listing create/edit, listing display, customer order, and farmer order pages for these capabilities.
- Do not add a payment gateway, paid API, new ML model, deployment redesign, or broad redesign of working modules.

## Capabilities

### New Capabilities

- `listing-media-upload`: Backend-mediated listing image upload, Cloudinary strategy, image validation, listing image persistence, ownership rules, and frontend upload/preview behavior.
- `item-level-order-fulfillment`: Item-level order status lifecycle, farmer/customer/admin fulfillment permissions, aggregate order status derivation, stock restoration, and frontend order management behavior.

### Modified Capabilities

- `analytics-dashboard`: Admin dashboard requirements change from generic analytics to real database-backed admin operational analytics.
- `farmer-marketplace`: Listing requirements change to support uploaded listing images and item-level fulfillment details on marketplace orders.
- `auth-and-rbac`: RBAC requirements change to include admin analytics access and listing image/order-item ownership enforcement.
- `frontend-user-flows`: Frontend requirements change to add `/admin/dashboard`, listing image upload UI, listing image display, and item-level order status views/actions.

## Impact

- Backend: new admin analytics router/service/schemas; upload service/router; Cloudinary integration isolated behind a backend adapter; listing image model/schema; order item status fields and status update endpoint; marketplace order serialization updates; RBAC/ownership checks.
- Database: migration for listing images and `OrderItem` status/status timestamp fields, plus indexes for analytics queries and media ownership lookups.
- Frontend: `/admin/dashboard`; listing create/edit image upload and preview; listing card/detail image display; customer order item statuses; farmer order item status actions; admin-only route protection.
- Configuration: optional `CLOUDINARY_URL`, backend-only; optional upload size setting if useful.
- Tests/verification: backend aggregate tests, upload validation/ownership tests, item-level status tests, migration validation, frontend typecheck/build, Docker config/start checks, and manual Cloudinary-unconfigured behavior verification.
