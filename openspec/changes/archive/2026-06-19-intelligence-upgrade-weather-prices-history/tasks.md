## 1. Database Models and Migrations

- [x] 1.1 Add backend SQLAlchemy models for `CropPriceRecord`, optional `PriceSource`, optional `CropPriceImportLog`, and `RecommendationHistory`.
- [x] 1.2 Add Pydantic schemas for weather responses, weather-aware crop recommendation requests/responses, price trend responses, crop catalog responses, and recommendation history list/detail responses.
- [x] 1.3 Register new models in backend model imports and Alembic metadata.
- [x] 1.4 Generate an Alembic migration for price records, optional source/import tables, and recommendation history with ownership/query indexes.
- [x] 1.5 Manually inspect migration for UUID foreign keys, JSON columns, date indexes, sample/source fields, cascade behavior, and downgrade safety.

## 2. Weather Adapter and API

- [x] 2.1 Add a backend weather service adapter interface and a free/no-key Open-Meteo-style implementation.
- [x] 2.2 Normalize weather fields: temperature, humidity when available, rainfall/precipitation, forecast window, latitude, longitude, timestamp, provider name, and provider status.
- [x] 2.3 Implement controlled unavailable/fallback result handling for weather provider failures and invalid provider responses.
- [x] 2.4 Add and register a weather router with `GET /api/v1/weather/current?lat=&lon=`.
- [x] 2.5 Add backend tests for weather success normalization and unavailable provider behavior using mocked adapter responses.

## 3. Weather-Aware Crop Recommendations

- [x] 3.1 Add `POST /api/v1/recommendations/crop/weather-aware` or extend the existing crop endpoint with optional weather fields without breaking current crop recommendation behavior.
- [x] 3.2 Resolve weather coordinates from explicit request lat/lon or authenticated Farmer profile coordinates when explicit coordinates are omitted.
- [x] 3.3 Ensure weather-aware crop recommendation uses weather context only when available and sets `used_weather=true` in the response.
- [x] 3.4 Ensure weather-aware crop recommendation falls back to normal/demo recommendation when weather is unavailable and sets `used_weather=false` with a clear warning/status.
- [x] 3.5 Avoid fake ML accuracy claims; only pass weather context into ML service if it fits the existing model contract cleanly, otherwise annotate the backend response.
- [x] 3.6 Add backend tests for weather-used success, weather-unavailable fallback, and Farmer profile coordinate fallback.

## 4. Price Trend Backend

- [x] 4.1 Add a price data provider/service abstraction that reads from database records and can later support imported/live providers.
- [x] 4.2 Add seeded sample/demo price data or a controlled seed script for initial mandi price records.
- [x] 4.3 Implement `GET /api/v1/prices/crops` to return distinct crop names and metadata for available price records.
- [x] 4.4 Implement `GET /api/v1/prices/trends?crop=&market=&state=&days=` with filtering, ordering, source, unit, and `is_sample` fields.
- [x] 4.5 Return controlled no-data/unavailable responses when no price records or provider data are available.
- [x] 4.6 Add optional `POST /api/v1/admin/prices/import` only if CSV import remains small and controlled; otherwise document seeded sample data as the phase strategy.
- [x] 4.7 Add backend tests for crop catalog, trend filtering, sample/demo labeling, and no-data behavior.

## 5. Recommendation History Backend

- [x] 5.1 Add recommendation history service helpers for saving authenticated crop, fertilizer, and disease recommendation requests/results.
- [x] 5.2 Update crop recommendation endpoint(s) to save authenticated history with input payload, result payload, model status, weather usage flag, and user id.
- [x] 5.3 Update fertilizer recommendation endpoint to save authenticated history.
- [x] 5.4 Update disease detection endpoint to save authenticated history without storing large image binary data in the history payload.
- [x] 5.5 Add and register recommendation history endpoints: `GET /api/v1/recommendations/history`, `GET /api/v1/recommendations/history/{id}`, and `DELETE /api/v1/recommendations/history/{id}`.
- [x] 5.6 Enforce ownership so users can only view/delete their own recommendation history records.
- [x] 5.7 Add backend tests for history persistence, own-history listing/detail, cross-user access blocking, and delete ownership.

## 6. Frontend Weather-Aware Crop UI

- [x] 6.1 Update crop recommendation UI to allow optional weather context through explicit location input and, for Farmers, profile-location usage where available.
- [x] 6.2 Display whether weather was used, unavailable, or skipped in the crop recommendation result.
- [x] 6.3 Ensure normal crop recommendation UI still works when weather data fails or is not requested.
- [x] 6.4 Add frontend loading/error states for weather-aware recommendation calls.

## 7. Frontend Price Trends

- [x] 7.1 Add `/prices` route with crop list/search, trend summaries, source labels, and sample/demo disclaimers.
- [x] 7.2 Add `/prices/[crop]` route with crop-specific price trend records, market/state filters where simple, source, unit, date, and sample/live status.
- [x] 7.3 Add controlled no-data/unavailable UI for crops or filters with no price records.
- [x] 7.4 Add navigation or homepage/advisory entry point to `/prices`.

## 8. Frontend Recommendation History

- [x] 8.1 Add `/recommendations/history` route for authenticated users with recommendation type, date, model status, and weather-used indicator.
- [x] 8.2 Add `/recommendations/history/[id]` detail route showing saved input and result payloads in a readable format.
- [x] 8.3 Add delete action for a user's own history item with success/error feedback.
- [x] 8.4 Add navigation or recommendation-page entry point to recommendation history for authenticated users.

## 9. Data Accuracy, Fallbacks, and Scope Guardrails

- [x] 9.1 Ensure weather API failures do not block normal/demo crop recommendations and do not display fabricated weather data.
- [x] 9.2 Ensure price UI and API clearly label seeded/sample/demo data and do not present it as live market data.
- [x] 9.3 Ensure live/external price provider unavailability returns controlled unavailable/no-data states.
- [x] 9.4 Confirm no paid APIs, Cloudinary upload, admin analytics dashboard, or item-level fulfillment features were added.

## 10. Tests and Verification

- [x] 10.1 Run backend tests with `cd backend && PYTHONPATH=. pytest app/tests/test_backend.py`.
- [x] 10.2 Run ML service tests with `cd ml_service && PYTHONPATH=.. pytest tests/test_ml.py`.
- [x] 10.3 Run frontend checks with `cd frontend && npm run lint && npx tsc --noEmit && npm run build`.
- [x] 10.4 Validate migrations with `cd backend && alembic upgrade head` against a clean database.
- [x] 10.5 Validate Docker configuration with `docker compose config`.
- [x] 10.6 Manually verify weather fallback by forcing weather provider unavailable and confirming crop recommendation still returns with `used_weather=false`.
- [x] 10.7 Manually verify price pages show sample/demo disclaimers for seeded sample records.
- [x] 10.8 Document known limitations and exact verification results in the final implementation summary.
