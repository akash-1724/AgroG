## Context

AgroGuide currently has authenticated users, farmer marketplace listings, carts, orders, reviews, educational resources, crop/fertilizer/disease advisory flows, price trends, recommendation history, and Dockerized services. Previous phases intentionally deferred admin analytics, real listing media upload, and item-level fulfillment. This phase adds those final product polish features without changing the project structure or adding paid services, payment gateways, new ML models, or broad redesigns.

Current constraints:
- Keep the repository structure: `frontend/`, `backend/`, `ml_service/`, `openspec/`, `docker-compose.yml`.
- Use real database data for analytics; do not hardcode fake metrics.
- Keep Cloudinary optional and backend-only through `CLOUDINARY_URL`.
- Keep the marketplace/order model understandable for a small project.
- Do not redesign already working pages unless required for the new capability.

## Goals / Non-Goals

**Goals:**
- Add an admin-only analytics overview backed by real DB aggregates.
- Add listing image upload through the backend with secure Cloudinary handling when configured.
- Validate image MIME type, extension, and size before upload/storage.
- Persist listing images and display them on listing cards/details and listing create/edit flows.
- Add item-level fulfillment statuses so multi-farmer cart orders are manageable.
- Enforce ownership: farmers can manage only their listing images and order items; admins can manage all.
- Keep migrations, tests, and verification commands explicit.

**Non-Goals:**
- No payment gateway or payment state machine.
- No paid APIs or paid media storage requirement.
- No new ML models or model retraining.
- No deployment redesign or managed infrastructure setup.
- No broad UI redesign of existing working modules.
- No complex charting dependency unless an existing/lightweight option is already present.
- No full audit/event sourcing system beyond simple timestamps/status fields.

## Decisions

### Admin Analytics: Real Aggregates in a Backend Service

Add admin analytics under `GET /api/v1/admin/analytics/overview`, implemented as a backend service that queries existing tables and returns counts/summaries. Optional detail endpoints, such as `/admin/analytics/orders` and `/admin/analytics/ml-usage`, can be added only if they remain small and avoid duplicating the overview.

Overview response should include:
- total users and users by role
- new users over time
- total listings and listings by status/category
- total orders and orders by status
- order value summary
- crop/fertilizer recommendation usage
- disease detection usage
- recommendation history usage if useful
- educational resource count if the table exists
- review/rating summary if reviews exist

Rationale: analytics belong in the backend where RBAC and database aggregation are enforceable. Frontend should render cards/tables first; charts are optional.

Alternatives considered:
- Compute analytics in frontend by fetching many endpoints: rejected because it leaks complexity and can bypass admin-only aggregation boundaries.
- Hardcode demo analytics: rejected by acceptance criteria.

### Image Upload: Backend-Mediated Cloudinary Adapter

Add an upload service adapter with a Cloudinary implementation enabled only when `CLOUDINARY_URL` is configured. Frontend uploads files to backend endpoints; the backend validates the file, uploads it to Cloudinary, and stores the returned secure URL. Cloudinary secrets remain backend-only.

Endpoints:
- `POST /api/v1/uploads/listing-image` for temporary/direct upload if useful.
- `POST /api/v1/marketplace/listings/{id}/images` for attaching an uploaded image to a listing.
- `DELETE /api/v1/marketplace/listings/{id}/images/{image_id}` for removing a listing image.

If Cloudinary is not configured, the backend should return a controlled configuration error. A local development fallback may be used only if it is simple, explicit, and does not pretend to be production storage.

Rationale: backend-mediated uploads prevent frontend exposure of Cloudinary secrets and keep ownership validation in one place.

Alternatives considered:
- Pasted image URLs: rejected because the phase goal is real upload storage.
- Unsigned direct browser upload: deferred because safe preset configuration adds setup ambiguity.
- Store images as database blobs: rejected as unnecessary and inefficient for this project.

### Listing Image Persistence: Dedicated `ListingImage` Table

Use a dedicated table instead of a JSON column where feasible:
- `listing_images`: id, listing_id, image_url, public_id, alt_text, sort_order, is_primary, created_at.

Rationale: multiple images, deletion by image id, primary image selection, and Cloudinary public IDs are cleaner with a table. If implementation complexity becomes an issue, a minimal `image_urls` JSON approach is acceptable only if deletion/ownership behavior remains testable.

### Item-Level Fulfillment: Add Status to `OrderItem`

Prefer item-level fulfillment over splitting checkout into farmer-specific orders because the existing cart checkout and order history already create a single customer order containing multiple items. Adding `OrderItem.status`, `status_updated_at`, and optional `fulfilled_at` is smaller and preserves existing customer order semantics.

Order item status lifecycle:
- `pending`
- `accepted`
- `rejected`
- `ready`
- `completed`
- `cancelled`

Status rules:
- Farmer can update only order items tied to their own crop listings.
- Customer can view aggregate order status and each item status.
- Admin can update/manage all order items.
- Order aggregate status is derived from item statuses.
- Rejected/cancelled items restore stock when appropriate and only once.

Rationale: a single order with item-level status handles multi-farmer carts without introducing order grouping complexity or changing checkout UX dramatically.

Alternatives considered:
- Split checkout into farmer-specific orders: simpler conceptually, but more disruptive to current cart checkout, customer order history, and review flow.
- Keep only order-level status: rejected because multi-farmer carts need per-farmer fulfillment control.

### RBAC / Ownership Matrix

Admin analytics:
- Admin: view all analytics.
- Farmer/customer/anonymous: denied.

Listing images:
- Listing-owner farmer: upload/delete images for own listing.
- Other farmers/customers/anonymous: denied.
- Admin: upload/delete any listing image.

Order items:
- Listing-owner farmer: view/update own order items only.
- Customer: view their order and item statuses; no farmer fulfillment updates.
- Admin: view/update all order items.
- Anonymous: denied.

### Frontend Plan

Add `/admin/dashboard` as an admin-only route. It should use cards/tables first and optionally simple visual bars if no chart dependency is needed.

Update listing create/edit forms to upload images through backend and preview results. Listing cards/details should display primary uploaded image or a safe placeholder.

Update customer orders to show item-level statuses. Update farmer orders to show only farmer-owned order items with status action buttons.

## Risks / Trade-offs

- [Risk] Cloudinary not configured during local development -> Mitigation: return clear backend configuration error and document required env var; optionally use explicit local fallback if already simple.
- [Risk] Upload secrets leak to frontend -> Mitigation: never use `CLOUDINARY_URL` in frontend env; route uploads through backend.
- [Risk] Status transitions become inconsistent -> Mitigation: centralize transition validation and aggregate order status derivation in backend helpers.
- [Risk] Stock restoration can double-restore -> Mitigation: restore stock only on transition into `rejected`/`cancelled` from non-terminal statuses and test it.
- [Risk] Analytics queries become slow as data grows -> Mitigation: use aggregate SQL, indexes, and small time buckets; acceptable for small project scale.
- [Risk] UI scope expands into dashboard redesign -> Mitigation: cards/tables first; charts optional.

## Migration Plan

1. Add backend models/schemas for listing images and order item fulfillment fields.
2. Add Alembic migration for `listing_images`, `OrderItem.status`, `status_updated_at`, optional `fulfilled_at`, and useful indexes.
3. Backfill existing order items to `pending` or a status derived from existing order status.
4. Add analytics service/router and admin-only dependencies.
5. Add upload adapter/service/router and marketplace listing image endpoints.
6. Add item status transition helper and order aggregate status derivation helper.
7. Update marketplace/order routers and schemas to expose item statuses and listing images.
8. Update frontend admin dashboard, listing forms, listing display, customer orders, and farmer orders.
9. Run backend tests, frontend lint/typecheck/build, migration validation, Docker config/start, and manual upload/fulfillment checks.

Rollback strategy:
- Hide frontend links to `/admin/dashboard` and image upload controls.
- Keep existing listing/order flows using placeholders and order-level status if needed.
- Use Alembic downgrade only before production data depends on uploaded image/order item status records.

## Open Questions

- Should local file storage be implemented as a development fallback when Cloudinary is absent, or should missing `CLOUDINARY_URL` always return a controlled error? Default: controlled error unless a simple existing static-file pattern exists.
- Should order item status transitions be strict (`pending -> accepted/rejected -> ready -> completed`) or permissive for admins? Default: farmers get strict transitions; admins can correct status with validation.
- Should uploaded images support manual primary image selection in this phase? Default: first image becomes primary; simple reorder/primary update only if low effort.
