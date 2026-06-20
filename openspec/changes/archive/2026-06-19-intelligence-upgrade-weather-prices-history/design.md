## Context

AgroGuide currently has authenticated advisory flows, crop/fertilizer recommendation pages, plant disease detection, farmer profiles with coordinates, and an ML service. The previous commerce phase adds marketplace trust and public farmer profiles. This phase improves advisory intelligence without claiming accuracy that the system cannot prove and without adding paid external APIs.

The project structure remains fixed: `frontend/`, `backend/`, `ml_service/`, `openspec/`, and `docker-compose.yml`. Existing recommendation endpoints and ML service contracts should be reused where practical. External weather and price providers must be hidden behind service adapters so sample data, live data, or unavailable states can be swapped without changing API contracts.

## Goals / Non-Goals

**Goals:**
- Add optional weather context to crop recommendations.
- Prefer a free/no-key weather provider, using an Open-Meteo-style adapter if suitable.
- Preserve normal/demo crop recommendation behavior when weather is unavailable.
- Clearly expose whether weather data was used and what weather fields were used.
- Add crop price trend APIs and UI using live, imported, or clearly marked sample/demo records.
- Add authenticated recommendation history storage and frontend history pages.
- Enforce recommendation history ownership.
- Keep integrations adapter-backed and testable.
- Provide migrations, tests, and verification commands.

**Non-Goals:**
- No paid weather or price APIs.
- No fake live market prices.
- No claims of improved ML accuracy unless model behavior is actually changed and validated.
- No Cloudinary upload.
- No admin analytics dashboard.
- No item-level fulfillment.
- No full notification system.
- No complex forecasting model training in this phase.

## Decisions

### Weather Integration: Backend Adapter with Open-Meteo-Style Default

Add a backend weather adapter interface, for example `WeatherProvider`, with a concrete free/no-key HTTP implementation and a graceful unavailable result type. The default provider should prefer Open-Meteo-style current/forecast endpoints because they are free and do not require an API key.

The backend should expose `GET /api/v1/weather/current?lat=&lon=` and support `POST /api/v1/recommendations/crop/weather-aware`. The weather-aware crop endpoint should accept explicit latitude/longitude, and may fall back to authenticated farmer profile coordinates when available. If weather lookup fails, the endpoint should still return a crop recommendation using existing normal/demo logic and set `used_weather=false` with a clear warning or provider status.

Alternatives considered:
- Put weather calls in the frontend: rejected because it duplicates fallback logic and exposes provider details.
- Require a weather API key: rejected because this phase prefers free/no-key APIs.
- Change the ML service contract deeply: deferred because model accuracy must not be faked. Weather context can be passed only if the existing model input contract supports it cleanly; otherwise backend response annotates weather context separately.

### Weather Fields and Disclosure

Normalize weather data into one schema containing temperature, humidity when available, rainfall/precipitation, forecast window, latitude, longitude, timestamp, provider name, and provider status. Recommendation responses must include `used_weather`, optional `weather`, and optional `weather_warning`/`provider_status` fields.

Rationale: users need to know whether advice used live weather or fell back to normal mode.

### Price Trend Data Source Strategy

Use database-backed `CropPriceRecord` rows as the canonical query source. Start with seeded sample/demo mandi price records or an optional CSV/manual import. Add an adapter/service boundary such as `PriceDataProvider` so future live providers can populate the same schema.

Every record must include `source` and `is_sample`. UI and API responses must expose `is_sample` and a data disclaimer. If no data exists for a query, return an empty result with a controlled unavailable/no-data state instead of invented prices.

Alternatives considered:
- Scrape market sites live: rejected as fragile and potentially unreliable.
- Depend on a paid market API: rejected by scope.
- Hardcode prices in frontend: rejected because it hides source and sample status.

### Price Trend Schema and APIs

Add tables for crop price records and optional import/source tracking:
- `crop_price_records`: crop name, market, district, state, min/max/modal price, unit, recorded date, source, `is_sample`, timestamps.
- `price_sources`: optional source metadata if useful for provider labels and import provenance.
- `crop_price_import_logs`: optional admin/import log if CSV import stays small.

Add public/read APIs:
- `GET /api/v1/prices/trends?crop=&market=&state=&days=`
- `GET /api/v1/prices/crops`

Add `POST /api/v1/admin/prices/import` only if CSV import remains small and controlled; otherwise seed sample data through migration/seed script and leave admin import out of implementation.

### Recommendation History

Persist authenticated recommendation requests/results in a `recommendation_history` table for crop, fertilizer, and disease flows. Store `recommendation_type`, `input_payload`, `result_payload`, `model_status`, `used_weather`, `created_at`, and `user_id`.

Existing recommendation endpoints should save history only when the caller is authenticated. Anonymous users can still use public/demo endpoints if they already can, but no history is created. Users can list, view, and delete only their own history. Admin aggregate usage is out of scope.

Alternatives considered:
- Store only a minimal text summary: rejected because detail pages need input/result replay.
- Store history in browser localStorage: rejected because ownership and cross-device behavior matter.

### Frontend Routes and UX

Add:
- `/prices`: searchable/listed crop price trend page with sample/live/unavailable labels.
- `/prices/[crop]`: focused crop trend page with market/state filters if simple.
- `/recommendations/history`: authenticated user's recommendation history list.
- `/recommendations/history/[id]`: history detail view.

Update crop recommendation UI to optionally use location/weather, including an explicit weather-used badge or fallback warning. Update navigation with price/history entry points where appropriate.

### Data Accuracy and Disclaimer Rules

Weather and price responses must not imply unavailable data was used. Sample price data must be labeled as sample/demo in backend response and frontend UI. Weather-aware recommendations must explicitly indicate whether weather was used. Price pages must show source, date, unit, and sample/live status.

## Risks / Trade-offs

- [Risk] Free weather provider changes or downtime can break weather lookup → Mitigation: adapter returns unavailable state and crop recommendation falls back to normal mode.
- [Risk] Sample price data may be mistaken for live prices → Mitigation: persist and display `is_sample`, source, and a demo disclaimer.
- [Risk] Recommendation history may store sensitive user inputs → Mitigation: enforce ownership, avoid public exposure, and allow users to delete entries.
- [Risk] JSON payload history can grow without bound → Mitigation: keep payloads compact and add pagination to history list.
- [Risk] Weather context may not map cleanly to current ML model inputs → Mitigation: do not fake accuracy; include weather as context/disclosure unless model contract supports direct use.
- [Risk] CSV admin import can expand scope → Mitigation: prefer seeded sample data unless import is small and controlled.

## Migration Plan

1. Add backend models/schemas for weather response DTOs, crop price records, optional price source/import logs, and recommendation history.
2. Generate and inspect Alembic migration for new tables, JSON columns, indexes, and downgrade safety.
3. Add service adapters for weather and price data.
4. Add weather, price, and history routers and register them under `/api/v1`.
5. Update existing recommendation endpoints to save authenticated history.
6. Add frontend price and history routes, plus weather-aware crop recommendation controls.
7. Seed sample price data or add controlled CSV import if small.
8. Run backend tests, ML tests, frontend lint/typecheck/build, migration validation, and Docker config validation.

Rollback strategy:
- Disable frontend links to new price/history/weather-aware pages.
- Keep new tables unused while investigating issues.
- Alembic downgrade can remove new tables if no production data preservation is required.

## Open Questions

- Should weather-aware crop recommendations pass normalized weather fields into the ML service, or should the backend simply annotate existing recommendations with weather context in this phase? Default: only pass fields if it fits the existing model contract without pretending accuracy.
- Should CSV price import be implemented now, or should seeded sample data be enough for this phase? Default: use seeded sample data first; add import only if time remains and it stays controlled.
- Should farmers with profile coordinates get one-click weather-aware recommendations by default? Default: yes for authenticated farmers, while still allowing explicit lat/lon input.
