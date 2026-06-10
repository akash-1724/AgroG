# Crop Recommendation Specification

## Purpose
Initial definition of the Crop Recommendation capability for AgroGuide.

## Requirements

### Requirement: Soil and Weather Metric Submission
The system SHALL allow users to submit soil parameters (Nitrogen N, Phosphorus P, Potassium K, pH level) and local weather metrics (temperature, humidity, rainfall) to retrieve crop recommendations.

#### Scenario: Submitting Valid Parameters
- **WHEN** a user submits N, P, K, pH, temperature, humidity, and rainfall values within valid ranges
- **THEN** the system SHALL process the values through the ML model and return a ranked list of recommended crops

### Requirement: ML Prediction Caching
The system SHALL cache crop recommendation predictions in Redis using a hash of the input parameters to improve response latency.

#### Scenario: Retrieving Cached Recommendation
- **WHEN** a user requests a recommendation with parameters matching an active cache key in Redis
- **THEN** the system SHALL return the cached response without calling the ML model
