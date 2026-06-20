## 1. Database Models and Migrations

- [x] 1.1 Add backend SQLAlchemy models for `Cart`, `CartItem`, and `Review` with relationships to `User`, `CropListing`, `Order`, and `OrderItem` where applicable.
- [x] 1.2 Add Pydantic schemas for cart responses, cart item mutations, checkout response, review creation, review response, rating summary, and public farmer profile response.
- [x] 1.3 Register new models in backend model imports so Alembic metadata includes cart and review tables.
- [x] 1.4 Generate an Alembic migration for `carts`, `cart_items`, and `reviews` with ownership indexes, cart/listing uniqueness, and duplicate-review lookup support.
- [x] 1.5 Manually inspect and adjust the migration for UUID foreign keys, cascade behavior, uniqueness constraints, rating constraints where practical, and downgrade safety.

## 2. Cart Backend API

- [x] 2.1 Add a backend cart router and register it under `/api/v1/cart`.
- [x] 2.2 Implement `GET /api/v1/cart` to create/read the current Customer cart and return enriched item, listing, farmer, subtotal, and estimated total data.
- [x] 2.3 Implement `POST /api/v1/cart/items` to add or merge an active listing into the authenticated Customer cart.
- [x] 2.4 Implement `PATCH /api/v1/cart/items/{id}` to update quantity with ownership, positive quantity, listing status, and stock validation.
- [x] 2.5 Implement `DELETE /api/v1/cart/items/{id}` and `DELETE /api/v1/cart/clear` with customer ownership enforcement.
- [x] 2.6 Implement `POST /api/v1/cart/checkout` to validate all cart items, lock listing rows, create existing `Order`/`OrderItem` records, deduct stock, clear the cart, and return the created order.
- [x] 2.7 Ensure farmers, anonymous users, and non-owning customers cannot mutate another Customer's cart.

## 3. Farmer Public Profile Backend API

- [x] 3.1 Add public farmer profile response assembly that includes farm name, farmer name, approximate address/location, description, active listings, rating summary, review count, and recent reviews.
- [x] 3.2 Implement `GET /api/v1/farmers/{farmer_id}/public` without exposing sensitive exact coordinates.
- [x] 3.3 Implement `GET /api/v1/farmers/{farmer_id}/listings` to return only active listings for the Farmer.
- [x] 3.4 Add or extend `PATCH /api/v1/farmers/me/profile` so Farmers can edit their own farm name, address/location text, district/city/state, description, and visibility fields.
- [x] 3.5 Ensure Farmers cannot edit other Farmers' profiles and public users cannot access private profile fields.

## 4. Reviews and Ratings Backend API

- [x] 4.1 Add a reviews router and register it under `/api/v1/reviews`.
- [x] 4.2 Implement `POST /api/v1/reviews` for Customer-only review creation with rating 1-5 and comment validation.
- [x] 4.3 Validate review eligibility by requiring a completed order item owned by the Customer and connected to the target Farmer/listing.
- [x] 4.4 Prevent duplicate reviews for the same Customer/order item/listing combination.
- [x] 4.5 Block Farmers from reviewing themselves or their own listings.
- [x] 4.6 Implement `GET /api/v1/reviews/farmers/{farmer_id}` and `GET /api/v1/reviews/listings/{listing_id}` with pagination.
- [x] 4.7 Implement `DELETE /api/v1/reviews/{id}` for Admin moderation.
- [x] 4.8 Add rating summary helper queries for Farmer and listing average/count derived from review rows.

## 5. Frontend Cart Flow

- [x] 5.1 Add a `/cart` route showing item name, farmer, unit price, quantity controls, subtotal, estimated total, remove, clear, and checkout actions.
- [x] 5.2 Update listing cards and listing detail pages to use add-to-cart instead of direct order placement.
- [x] 5.3 Add cart API client calls and loading/error/empty states.
- [x] 5.4 Ensure checkout from `/cart` validates stock via backend response and shows success/failure toasts.
- [x] 5.5 Add a navbar/mobile-menu cart link or prominent entry point for authenticated Customers.

## 6. Frontend Farmer Profiles and Reviews

- [x] 6.1 Add `/farmers/[id]` route with farmer header, approximate location, description, rating summary, active listings, and reviews.
- [x] 6.2 Link listing cards and listing detail pages to `/farmers/{farmer_id}` when farmer data is available.
- [x] 6.3 Show derived rating average/count on listing cards and listing detail pages.
- [x] 6.4 Add review lists to farmer profile and listing detail pages.
- [x] 6.5 Add review form entry points for eligible completed purchases in customer order/history UI.
- [x] 6.6 Add optional farmer profile edit UI only if existing farmer profile/location UI cannot cover required profile fields cleanly.

## 7. Tests and Verification

- [x] 7.1 Add backend tests for cart add/update/remove/clear, ownership blocking, stock validation, and successful checkout clearing the cart.
- [x] 7.2 Add backend tests for public farmer profile visibility, active listing filtering, and hidden exact coordinates.
- [x] 7.3 Add backend tests for review eligibility, duplicate prevention, farmer self-review blocking, rating aggregation, and admin moderation.
- [x] 7.4 Run backend tests with `cd backend && PYTHONPATH=. pytest app/tests/test_backend.py`.
- [x] 7.5 Run ML service tests with `cd ml_service && PYTHONPATH=.. pytest tests/test_ml.py` to confirm unrelated ML service remains stable.
- [x] 7.6 Run frontend checks with `cd frontend && npm run lint && npx tsc --noEmit && npm run build`.
- [x] 7.7 Validate migrations with `cd backend && alembic upgrade head` against a clean database.
- [x] 7.8 Validate Docker configuration with `docker compose config`.

## 8. Scope Guardrails

- [x] 8.1 Confirm no payment gateway, payment status flow, or external payment dependency was added.
- [x] 8.2 Confirm no weather, price analytics, Cloudinary upload, admin analytics, or item-level fulfillment features were added in this phase.
- [x] 8.3 Document any manual verification steps or known limitations in the final implementation summary.
