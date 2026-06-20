## Context

AgroGuide already has authentication/RBAC, marketplace listings, order creation, farmer location data, advisory ML pages, and basic frontend flows. The current commerce flow still feels direct and low-trust: listing detail pages can lead straight to ordering, farmer context is fragmented, and buyers cannot leave verified feedback after completed purchases.

This phase upgrades commerce UX and trust without expanding into payments, weather, price analytics, Cloudinary upload, admin analytics, or item-level fulfillment. The existing project shape remains unchanged: `frontend/`, `backend/`, `ml_service/`, `openspec/`, and `docker-compose.yml`.

## Goals / Non-Goals

**Goals:**
- Add a cart page before checkout with add, update quantity, remove, clear, stock validation, and checkout.
- Add public farmer profile pages with approximate location, profile details, active listings, rating summary, and review summary.
- Add review/rating creation for eligible customers after completed orders.
- Prevent duplicate reviews for the same purchased listing/order item where feasible.
- Compute farmer/listing rating summaries from review rows instead of manually edited rating fields.
- Keep implementation clean, small, and compatible with existing FastAPI/SQLAlchemy/Next.js patterns.

**Non-Goals:**
- No payment gateway or payment state machine.
- No weather-aware recommendations.
- No price trend analytics.
- No Cloudinary or file upload integration for listing images.
- No admin analytics dashboard.
- No item-level fulfillment redesign in this phase.
- No full notification system.

## Decisions

### Cart design: backend persistent cart
Use backend persistent cart tables for logged-in customers instead of localStorage-only cart.

Rationale:
- Existing auth/session flow is already stable enough for customer-owned resources.
- Checkout needs authoritative stock validation and current price/listing data.
- Backend ownership rules reduce accidental manipulation of cart item IDs.
- The cart remains available across browser sessions.

Alternative considered: client-side localStorage cart. This is simpler, but it pushes ownership and stock validation complexity to checkout and makes multi-device behavior poor. It also makes it easier for stale listings to remain in cart without server-side checks.

### Database schema
Add new backend models and migration:
- `carts`: `id`, `customer_id`, `created_at`, `updated_at`.
- `cart_items`: `id`, `cart_id`, `crop_listing_id`, `quantity`, `created_at`, `updated_at`.
- `reviews`: `id`, `customer_id`, `farmer_id`, nullable `listing_id`, nullable `order_id`, nullable `order_item_id`, `rating`, `comment`, `created_at`, `updated_at`.

Constraints and indexes:
- One active cart per customer using unique `carts.customer_id`.
- Unique cart item per cart/listing using unique `(cart_id, crop_listing_id)`.
- Review rating constrained to 1-5 at schema/API level; DB check constraint can be added if straightforward.
- Prevent duplicate reviews with unique `(customer_id, order_item_id, listing_id)` when `order_item_id` is available. If the DB cannot express partial uniqueness portably, enforce via application query before insert and add an index for lookup.
- Index review lookup by `farmer_id`, `listing_id`, and `customer_id`.

### API contracts
Add cart endpoints:
- `GET /api/v1/cart`: return current customer's cart with enriched item/listing/farmer data and estimated totals.
- `POST /api/v1/cart/items`: add listing and quantity; merge with existing cart item when same listing already exists.
- `PATCH /api/v1/cart/items/{id}`: update quantity; reject non-owned cart items.
- `DELETE /api/v1/cart/items/{id}`: remove one cart item; reject non-owned cart items.
- `DELETE /api/v1/cart/clear`: clear current customer's cart.
- `POST /api/v1/cart/checkout`: validate all items are active and in stock, then create order using existing marketplace order logic and clear cart on success.

Add farmer profile endpoints:
- `GET /api/v1/farmers/{farmer_id}/public`: public profile, approximate location/address, active listings, rating summary, review summary.
- `GET /api/v1/farmers/{farmer_id}/listings`: active public listings for one farmer.
- `PATCH /api/v1/farmers/me/profile`: allow a farmer to edit profile fields if current update endpoints do not cover farm name/description/address well enough.

Add review endpoints:
- `POST /api/v1/reviews`: customer-only; validates completed purchase eligibility and duplicate prevention.
- `GET /api/v1/reviews/farmers/{farmer_id}`: public farmer reviews with pagination.
- `GET /api/v1/reviews/listings/{listing_id}`: public listing reviews with pagination.
- `DELETE /api/v1/reviews/{id}`: admin moderation only; optionally owner delete if simple, but admin delete is enough for this phase.

### Frontend routes and components
Add or update frontend:
- `/cart`: cart table/cards with item name, farmer, unit price, quantity control, subtotal, estimated total, remove, clear, and checkout action.
- `/farmers/[id]`: public farmer profile, approximate location/address, description, rating summary, active produce/listings, reviews.
- Optional `/farmer/profile/edit`: farmer profile editor if existing farmer location/profile page is insufficient.
- Listing cards/details: replace direct order placement with add-to-cart and show rating summary.
- Order/history UI: show review form only for eligible completed purchases.

### RBAC and ownership matrix
- Public/anonymous: can view marketplace listings, public farmer profiles, listing/farmer review summaries, and published reviews.
- Customer: can manage only their own cart; can checkout their cart; can create reviews only for completed purchased items; cannot review the same purchased item repeatedly.
- Farmer: can view their public profile and reviews; can update own profile; cannot create reviews for self or modify customer reviews.
- Admin: can moderate/delete reviews and view regular marketplace/admin data.

### Rating computation
Ratings are derived from `reviews` rows using aggregate queries:
- Listing average/count from reviews with `listing_id`.
- Farmer average/count from reviews with `farmer_id`.

Do not store mutable rating summary fields in this phase unless repeated aggregate queries become a measurable issue. Existing `FarmerProfile.rating` can remain for backward compatibility but public responses should use computed review aggregates where available.

## Risks / Trade-offs

- [Risk] Backend persistent cart adds schema/API work compared to localStorage → Mitigation: keep one active cart per customer and simple CRUD endpoints.
- [Risk] Existing order model has global order status, which is imperfect for multi-farmer orders → Mitigation: checkout continues using existing backend order design; item-level fulfillment remains out of scope.
- [Risk] Duplicate review prevention can be tricky when legacy orders lack loaded listing/farmer context → Mitigation: base eligibility on completed `OrderItem` rows and enforce application-level duplicate checks.
- [Risk] Rating aggregates may be expensive as data grows → Mitigation: add indexes now; defer materialized summary fields until needed.
- [Risk] Public profiles can expose sensitive location data → Mitigation: return approximate address/city/state and avoid exact coordinates unless already intentionally public.

## Migration Plan

1. Add SQLAlchemy models and schemas for cart/cart items and reviews.
2. Generate and inspect Alembic migration for new tables, constraints, and indexes.
3. Add API routers and register them in `backend/app/api/v1/api.py`.
4. Add frontend routes/components and update marketplace links/actions.
5. Run backend tests, frontend lint/typecheck/build, ML tests, and Docker config validation.
6. Apply migrations in development/staging before exposing the new UI.

Rollback strategy:
- Revert frontend links/actions to direct marketplace behavior if needed.
- Keep new tables unused while investigating issues.
- Alembic downgrade can drop cart/review tables if no production data must be preserved.

## Verification Plan

- Backend tests:
  - Customer can add/update/remove/clear cart items.
  - Customer cannot access another customer's cart item.
  - Checkout rejects inactive/out-of-stock listings.
  - Checkout creates order/order items and clears cart on success.
  - Public farmer profile returns profile, active listings, and computed rating summary.
  - Review creation requires completed order item.
  - Duplicate review creation is blocked.
  - Farmer cannot review self-owned listing/farmer.
  - Admin can delete/moderate reviews.
- Frontend checks:
  - `npm run lint`
  - `npx tsc --noEmit`
  - `npm run build`
- Service checks:
  - `cd backend && PYTHONPATH=. pytest app/tests/test_backend.py`
  - `cd ml_service && PYTHONPATH=.. pytest tests/test_ml.py`
  - `docker compose config`

## Open Questions

- Should customers be able to edit/delete their own reviews, or should this phase keep only admin moderation? Default implementation should include admin delete and only add owner edit/delete if it stays small.
- Should cart checkout create one combined order for all items, preserving current design, or split per farmer? Default implementation should preserve current backend order design to avoid item-level fulfillment scope creep.
