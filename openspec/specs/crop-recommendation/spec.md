# Crop Recommendation Specification

## Purpose
Initial definition of the Crop Recommendation capability for AgroGuide.

## Requirements

### Requirement: Soil and Weather Metric Submission
The system SHALL allow users to submit soil parameters (Nitrogen N, Phosphorus P, Potassium K, pH level) and local weather metrics (temperature, humidity, rainfall) to retrieve crop recommendations. The system SHALL optionally support weather-aware crop recommendation using backend weather context, and weather-aware responses SHALL clearly disclose whether weather data was used.

#### Scenario: Submitting Valid Parameters
- **WHEN** a user submits N, P, K, pH, temperature, humidity, and rainfall values within valid ranges
- **THEN** the system SHALL process the values through the ML model and return a ranked list of recommended crops

#### Scenario: Weather-aware crop recommendation succeeds
- **WHEN** a user submits valid crop recommendation inputs with usable weather location context
- **THEN** the system SHALL return a crop recommendation with `used_weather=true` and normalized weather context

#### Scenario: Weather-aware crop recommendation falls back
- **WHEN** a user submits valid crop recommendation inputs but weather data is unavailable
- **THEN** the system SHALL return a crop recommendation with `used_weather=false` and a clear fallback status

#### Scenario: Authenticated crop recommendation history saved
- **WHEN** an authenticated user receives a crop recommendation
- **THEN** the system SHALL save the request and result in recommendation history

### Requirement: ML Prediction Caching
The system SHALL cache crop recommendation predictions in Redis using a hash of the input parameters to improve response latency.

#### Scenario: Retrieving Cached Recommendation
- **WHEN** a user requests a recommendation with parameters matching an active cache key in Redis
- **THEN** the system SHALL return the cached response without calling the ML model
