## 1. Database Migrations and Model Updates

- [x] 1.1 Update `CropListing` model in `backend/app/models/marketplace.py` to include `status` and `category` fields
- [x] 1.2 Generate and execute Alembic database migration applying updates to the `crop_listings` table

## 2. API Schema Verification

- [x] 2.1 Update Pydantic schemas in `backend/app/schemas/` to support category, status, and search/filter queries
- [x] 2.2 Define Pydantic request models for query filtering, sorting, pagination, and status patch requests

## 3. Marketplace Listings Endpoints & Security

- [x] 3.1 Implement search, category/availability filtering, sorting, and pagination in `GET /api/v1/marketplace/listings`
- [x] 3.2 Update `POST /api/v1/marketplace/listings` to validate and enforce that only Farmers can create listings
- [x] 3.3 Enforce ownership validation on `PUT/PATCH` and `DELETE` endpoints for crop listings (only owners can modify)

## 4. Orders Lifecycle & Safety Checks

- [x] 4.1 Implement transactional checkout in `POST /api/v1/marketplace/orders` using select `with_for_update` for stock checks and deduction
- [x] 4.2 Save price snapshot in `OrderItem.price_at_purchase` during order placement
- [x] 4.3 Lock down order detail endpoint `GET /api/v1/marketplace/orders/{id}` ensuring proper owner/privileged isolation
- [x] 4.4 Implement validation state machine and stock restoration logic in `PATCH /api/v1/marketplace/orders/{id}/status`

## 5. Verification & Documentation

- [x] 5.1 Create automated verification script `backend/verify_marketplace.py` testing list updates, RBAC, checkout race conditions, status paths, and stock restoration
- [x] 5.2 Document verification commands and update the main README file
