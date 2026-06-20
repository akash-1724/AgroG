# Weather-Aware Crop Recommendation Specification

## Purpose
Define optional weather lookup, fallback behavior, and disclosure for weather-aware crop recommendations.

## Requirements

### Requirement: Weather Service Adapter
The system SHALL provide a backend weather service adapter that retrieves normalized weather data from a free/no-key provider when available and returns a controlled unavailable state when the provider fails.

#### Scenario: Weather lookup succeeds
- **WHEN** a client requests current weather with valid latitude and longitude
- **THEN** the system SHALL return normalized weather fields including temperature, precipitation or rainfall when available, forecast window, latitude, longitude, timestamp, provider name, and provider status

#### Scenario: Weather lookup unavailable
- **WHEN** the weather provider cannot be reached or returns unusable data
- **THEN** the system SHALL return a controlled unavailable response without fabricating weather values

### Requirement: Weather-Aware Crop Recommendation
The system SHALL allow crop recommendations to optionally include weather context from explicit coordinates or the authenticated Farmer profile location when available.

#### Scenario: Recommendation uses weather data
- **WHEN** a user requests a weather-aware crop recommendation and weather data is available for the selected location
- **THEN** the response SHALL include the crop recommendation, normalized weather context, and `used_weather=true`

#### Scenario: Recommendation falls back without weather
- **WHEN** a user requests a weather-aware crop recommendation and weather data is unavailable
- **THEN** the system SHALL still return a normal/demo crop recommendation and include `used_weather=false` with a clear fallback warning or provider status

#### Scenario: Farmer profile location used
- **WHEN** an authenticated Farmer requests a weather-aware crop recommendation without explicit coordinates and their profile has coordinates
- **THEN** the system SHALL use the Farmer profile coordinates for weather lookup

### Requirement: Weather Data Disclosure
Weather-aware recommendation responses and frontend UI SHALL clearly show whether weather data was used and SHALL NOT imply weather was used when provider data was unavailable.

#### Scenario: Weather not used disclosure
- **WHEN** weather lookup fails during a recommendation request
- **THEN** the frontend SHALL display a fallback or unavailable message and avoid showing live-weather-based advice claims
