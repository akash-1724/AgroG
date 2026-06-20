## MODIFIED Requirements

### Requirement: Advisory Navigation
The frontend SHALL provide navigation paths for advisory features including crop recommendations, fertilizer recommendations, disease detection, price trends, and recommendation history where appropriate for the authenticated user.

#### Scenario: User sees price trend entry point
- **WHEN** a user views primary navigation or advisory landing content
- **THEN** the UI SHALL provide an entry point to `/prices`

#### Scenario: Authenticated user sees recommendation history entry point
- **WHEN** an authenticated user views advisory navigation or recommendation pages
- **THEN** the UI SHALL provide an entry point to `/recommendations/history`

#### Scenario: Weather disclosure visible in crop recommendation flow
- **WHEN** a user receives a weather-aware crop recommendation
- **THEN** the UI SHALL show whether weather data was used or unavailable
