## MODIFIED Requirements

### Requirement: Crop Recommendation Prediction
The system SHALL allow users to submit soil and environmental input data to receive a crop recommendation from the ML service. The system SHALL optionally support weather-aware crop recommendation using backend weather context, and weather-aware responses SHALL clearly disclose whether weather data was used.

#### Scenario: Successful crop recommendation
- **WHEN** a user submits valid crop recommendation inputs
- **THEN** the system SHALL return a crop recommendation and model/provider status

#### Scenario: Weather-aware crop recommendation succeeds
- **WHEN** a user submits valid crop recommendation inputs with usable weather location context
- **THEN** the system SHALL return a crop recommendation with `used_weather=true` and normalized weather context

#### Scenario: Weather-aware crop recommendation falls back
- **WHEN** a user submits valid crop recommendation inputs but weather data is unavailable
- **THEN** the system SHALL return a crop recommendation with `used_weather=false` and a clear fallback status

#### Scenario: Authenticated crop recommendation history saved
- **WHEN** an authenticated user receives a crop recommendation
- **THEN** the system SHALL save the request and result in recommendation history
