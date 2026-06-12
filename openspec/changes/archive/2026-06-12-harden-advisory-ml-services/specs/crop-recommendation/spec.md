## MODIFIED Requirements

### Requirement: Soil and Weather Metric Submission
The system SHALL allow users to submit soil parameters (Nitrogen N, Phosphorus P, Potassium K, pH level) and local weather metrics (temperature, humidity, rainfall) to retrieve crop recommendations.
The system SHALL validate that all input metrics are within realistic agronomic bounds:
- Nitrogen (N): 0 to 200
- Phosphorus (P): 0 to 200
- Potassium (K): 0 to 200
- pH level: 3.5 to 9.0
- Temperature: 0°C to 50°C
- Humidity: 10% to 100%
- Rainfall: 10mm to 500mm

If the crop recommendation ML model artifact is missing or fails to load, the system SHALL return a baseline fallback prediction clearly flagged with `model_status: "demo"`. All recommendations SHALL include an advisory disclaimer stating predictions are suggestions and not scientifically validated guarantees.

#### Scenario: Submitting Valid Parameters
- **WHEN** a user submits N, P, K, pH, temperature, humidity, and rainfall values within valid ranges
- **THEN** the system SHALL process the values through the ML model and return a ranked list of recommended crops along with `model_status` and an advisory disclaimer

#### Scenario: Submitting Out of Bound Parameters
- **WHEN** a user submits any metric outside the allowed range (e.g. pH = 1.0 or temperature = -10)
- **THEN** the system SHALL return a 422 validation error indicating the invalid field and bounds

#### Scenario: Model Artifact Missing Fallback
- **WHEN** the ML service is queried but the XGBoost model json artifact is missing from disk
- **THEN** the system SHALL return a demo crop recommendation list containing baseline crops, marked with `model_status: "demo"` and an advisory disclaimer
