## Why

AgroGuide currently supports marketplace listings and direct order creation, but the commerce experience feels incomplete because customers do not get a cart review step and buyers have limited trust signals before purchasing. This change upgrades the marketplace with a controlled cart flow, public farmer profiles, and review/rating features while keeping the project small and avoiding payments or unrelated analytics work.

## What Changes

- Add a cart-before-checkout flow so customers can add listing items, update quantities, remove items, review estimated totals, and check out only after stock validation.
- Add public farmer profile pages showing farm details, approximate location, active listings, rating summary, and review summary.
- Add review and rating support for completed purchases, including duplicate-review prevention and derived rating summaries.
- Add customer/farmer/admin ownership and moderation rules for cart, profile, and review operations.
- Add database migration coverage for cart and review entities, plus API contracts and frontend routes for the new commerce UX.
- Keep payment gateway, weather, price analytics, Cloudinary upload, admin analytics, and item-level fulfillment out of scope for this phase.

## Capabilities

### New Capabilities
- `commerce-cart`: Customer cart management, stock-validated checkout, and conversion from cart items to existing order/order item records.
- `farmer-public-profiles`: Public farmer profile pages with approximate location, active produce, profile details, and rating/review summaries.
- `commerce-reviews-ratings`: Customer review creation for eligible completed purchases, duplicate prevention, rating aggregation, review listing, and moderation rules.

### Modified Capabilities
- `farmer-marketplace`: Replace direct listing-detail order placement with cart-first checkout and surface rating summaries on listing cards/details.

## Impact

- Backend: new cart and review models, migrations, schemas, API routers, service logic for stock validation and eligibility checks, and updates to marketplace checkout behavior.
- Frontend: new `/cart`, `/farmers/[id]`, and optional `/farmer/profile/edit` routes; listing cards/details updated to add-to-cart and display ratings; review forms and review sections added where eligible.
- Database: new `carts`, `cart_items`, and `reviews` tables; indexes and uniqueness constraints for ownership and duplicate-review prevention.
- Tests and verification: backend tests for cart ownership, stock validation, checkout, review eligibility, duplicate prevention, and profile visibility; frontend build/lint/typecheck and manual commerce flow checks.
