## MODIFIED Requirements

### Requirement: Soil and Crop Type Submission
The system SHALL allow users to submit soil mineral ratios (N, P, K) along with target crop type to obtain fertilizer recommendations.
The system SHALL validate that N-P-K mineral inputs are within valid bounds (0 to 200). If the real fertilizer recommendation model pickle artifact is missing from disk, the system SHALL return a rule-based demo recommendation clearly marked as `model_status: "demo"`. Recommendations and guidelines SHALL include a safety warning disclaimer advising against dangerous chemical overdosage.

#### Scenario: Requesting Fertilizer Recommendations
- **WHEN** a user submits valid N, P, K levels and target crop type
- **THEN** the system SHALL process the values through the ML logic and return recommended fertilizer types, application guidelines, `model_status`, and a safety warning disclaimer

#### Scenario: Missing model file fallback
- **WHEN** a user requests a fertilizer recommendation but the Scikit-Learn model file is missing
- **THEN** the system SHALL return a rule-based fallback recommendation, marked with `model_status: "demo"` and a safety warning disclaimer
