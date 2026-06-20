## 1. Database Models and Migrations

- [x] 1.1 Add backend model for `ListingImage` with listing relationship, URL, storage public id, primary flag, sort order, alt text, and timestamps.
- [x] 1.2 Add `OrderItem` fulfillment fields: `status`, `status_updated_at`, optional `fulfilled_at`, and any stock-restoration guard needed to avoid double restore.
- [x] 1.3 Add backend schemas for listing images, upload responses/errors, admin analytics responses, order item status updates, and order responses with item statuses.
- [x] 1.4 Register new/changed models in backend imports and Alembic metadata.
- [x] 1.5 Generate Alembic migration for listing images, order item fulfillment fields, indexes, and backfill defaults for existing order items.
- [x] 1.6 Manually inspect migration for foreign keys, cascade behavior, defaults, indexes, downgrade safety, and existing data backfill.

## 2. Admin Analytics Backend

- [x] 2.1 Add admin analytics service that computes real database aggregates for users, roles, new users over time, listings, orders, order value, advisory usage, disease detection usage, resources, and reviews where available.
- [x] 2.2 Add analytics Pydantic response schemas with stable field names and empty/zero defaults for optional data.
- [x] 2.3 Add admin-only router with `GET /api/v1/admin/analytics/overview`.
- [x] 2.4 Add optional `GET /api/v1/admin/analytics/orders` only if it avoids duplicating overview logic.
- [x] 2.5 Add optional `GET /api/v1/admin/analytics/ml-usage` only if it avoids duplicating overview logic.
- [x] 2.6 Register admin analytics router under `/api/v1/admin`.
- [x] 2.7 Add backend tests for real aggregate values, empty optional data behavior, and non-admin access denial.

## 3. Listing Image Upload Backend

- [x] 3.1 Add backend upload configuration for maximum image size and supported MIME types/extensions.
- [x] 3.2 Add storage adapter interface and Cloudinary implementation using backend-only `CLOUDINARY_URL`.
- [x] 3.3 Add controlled error behavior when Cloudinary is not configured and no explicit local fallback is implemented.
- [x] 3.4 Add image validation helper for MIME type, extension, and file size before storage provider calls.
- [x] 3.5 Add upload/listing image endpoints: `POST /api/v1/marketplace/listings/{id}/images` and `DELETE /api/v1/marketplace/listings/{id}/images/{image_id}`.
- [x] 3.6 Add optional `POST /api/v1/uploads/listing-image` only if temporary upload is needed; otherwise keep uploads attached directly to listings.
- [x] 3.7 Enforce listing image ownership so only listing-owner Farmers or Admins can upload/delete images.
- [x] 3.8 Update listing create/update/read schemas and marketplace responses to include uploaded image metadata.
- [x] 3.9 Add backend tests for valid upload with mocked storage, invalid MIME/extension/size, missing Cloudinary config, owner upload/delete, other-farmer denial, and admin override.

## 4. Item-Level Fulfillment Backend

- [x] 4.1 Add order item status enum/validation for `pending`, `accepted`, `rejected`, `ready`, `completed`, and `cancelled`.
- [x] 4.2 Ensure checkout creates every order item with status `pending`.
- [x] 4.3 Add helper to validate allowed status transitions for Farmers and Admins.
- [x] 4.4 Add helper to derive aggregate order status from item statuses.
- [x] 4.5 Add helper to restore listing stock exactly once when an order item transitions into rejected/cancelled.
- [x] 4.6 Add `PATCH /api/v1/marketplace/order-items/{id}/status` with Farmer ownership enforcement and Admin override.
- [x] 4.7 Update order detail/list endpoints to include item-level fulfillment status and aggregate status.
- [x] 4.8 Update farmer order endpoint to return only farmer-owned order items or clearly scope visible items to the Farmer.
- [x] 4.9 Add backend tests for multi-farmer checkout, farmer own-item update, cross-farmer denial, admin update, customer status visibility, aggregate status derivation, and stock restoration without double restore.

## 5. Frontend Admin Dashboard

- [x] 5.1 Add `/admin/dashboard` route with admin-only guard using existing auth context patterns.
- [x] 5.2 Fetch `GET /api/v1/admin/analytics/overview` and render cards/tables for user, listing, order, order value, advisory, resource, and review metrics.
- [x] 5.3 Add loading, error, and non-admin blocked states for the dashboard.
- [x] 5.4 Add admin navigation entry point without exposing it as usable for non-admin users.

## 6. Frontend Listing Image Upload

- [x] 6.1 Update farmer listing create form to upload listing images through backend after or during listing creation.
- [x] 6.2 Update farmer listing edit form to upload, preview, and delete listing images.
- [x] 6.3 Show validation/storage errors clearly without losing listing form state.
- [x] 6.4 Update marketplace listing cards to display primary uploaded image or safe placeholder.
- [x] 6.5 Update listing detail page to display uploaded listing images.

## 7. Frontend Item-Level Fulfillment

- [x] 7.1 Update customer orders page or order detail UI to show aggregate order status and each order item status.
- [x] 7.2 Update farmer orders page to show farmer-owned order items and valid status action controls.
- [x] 7.3 Add UI feedback for item status update success/failure.
- [x] 7.4 Ensure multi-farmer order display remains understandable for customers and farmers.

## 8. Security and Scope Guardrails

- [x] 8.1 Confirm `CLOUDINARY_URL` and any Cloudinary secrets are backend-only and not used in frontend env variables.
- [x] 8.2 Confirm all admin analytics endpoints require Admin role.
- [x] 8.3 Confirm listing image endpoints enforce owner Farmer/Admin permissions.
- [x] 8.4 Confirm order item status endpoints enforce owner Farmer/Admin permissions and customer read-only status visibility.
- [x] 8.5 Confirm no payment gateway, paid API requirement, new ML model, deployment redesign, or broad UI redesign was added.

## 9. Tests and Verification

- [x] 9.1 Run backend tests with `cd backend && PYTHONPATH=. pytest app/tests/test_backend.py`.
- [x] 9.2 Run ML service tests with `cd ml_service && PYTHONPATH=.. pytest tests/test_ml.py`.
- [x] 9.3 Run frontend checks with `cd frontend && npm run lint && npx tsc --noEmit && npm run build`.
- [x] 9.4 Validate migrations with `cd backend && alembic upgrade head` against a clean database.
- [x] 9.5 Validate Docker configuration with `docker compose config`.
- [x] 9.6 Start Docker with `docker compose up -d --build` and verify frontend, backend, and ML health endpoints.
- [x] 9.7 Manually verify admin dashboard denies non-admin and displays real admin data for an Admin.
- [x] 9.8 Manually verify image upload configured/unconfigured behavior and confirm sample listing images render.
- [x] 9.9 Manually verify multi-farmer order item fulfillment with Farmer ownership checks and Customer item-status visibility.
- [x] 9.10 Document exact verification results, known limitations, and any Cloudinary/local fallback behavior in the final implementation summary.
