## Why

AgroGuide's advisory flows already provide crop, fertilizer, and disease recommendations, but they do not yet account for local weather, market price context, or a user's prior recommendation history. This change improves decision support while keeping data honesty explicit: weather and prices must be adapter-backed, clearly labeled, and resilient when external data is unavailable.

## What Changes

- Add optional weather-aware crop recommendations using a free/no-key weather service adapter, preferably Open-Meteo-style if feasible.
- Allow crop recommendations to continue in normal/demo mode when weather lookup fails, with responses clearly stating whether weather data was used.
- Add price trend analytics for crops using an adapter-based data-source strategy that can start with seeded/sample or imported mandi price records.
- Clearly label sample/demo price data and return controlled unavailable states when live/imported data is not available.
- Add authenticated recommendation history persistence for crop, fertilizer, and disease recommendation requests/results.
- Add frontend pages for price trends and recommendation history.
- Add database migration coverage for weather-aware recommendation metadata, crop price records, and recommendation history.
- Keep external integrations behind backend service adapters.
- Do not add paid APIs, Cloudinary upload, admin analytics dashboard, or item-level fulfillment in this phase.

## Capabilities

### New Capabilities

- `weather-aware-crop-recommendation`: Optional weather context for crop recommendations, weather adapter behavior, fallback rules, and response disclosure.
- `crop-price-trends`: Crop price record storage, source labeling, trend APIs, frontend price pages, and demo/live data honesty rules.
- `recommendation-history`: Authenticated recommendation history persistence, ownership rules, retrieval, deletion, and frontend history pages.

### Modified Capabilities

- `crop-recommendation`: Existing crop recommendation behavior gains optional weather-aware execution and must save authenticated recommendation history.
- `fertilizer-recommendation`: Existing fertilizer recommendation behavior must save authenticated recommendation history.
- `plant-disease-detection`: Existing disease detection behavior must save authenticated recommendation history.
- `frontend-user-flows`: Frontend navigation and advisory pages add price trends and recommendation history entry points.

## Impact

- Backend: new weather, price, and recommendation-history models/schemas/services; adapter interfaces; new weather and price endpoints; recommendation endpoint changes for optional weather and history persistence.
- ML service: no fake accuracy changes; may receive optional weather-derived context only if backend and current ML contract support it cleanly, otherwise backend response annotates weather context separately.
- Frontend: new `/prices`, `/prices/[crop]`, `/recommendations/history`, and `/recommendations/history/[id]` routes; crop recommendation UI additions for optional weather context and weather-used disclosure.
- Database: new tables for crop price records, optional price sources/import logs, and recommendation history; migration required.
- External APIs: optional free/no-key weather provider adapter; no paid API dependency.
- Verification: backend tests, migration validation, frontend lint/typecheck/build, ML tests, Docker config validation, and manual fallback checks for unavailable weather/price sources.
