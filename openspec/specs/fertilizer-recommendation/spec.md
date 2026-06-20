# Fertilizer Recommendation Specification

## Purpose
Initial definition of the Fertilizer Recommendation capability for AgroGuide.

## Requirements

### Requirement: Soil and Crop Type Submission
The system SHALL allow users to submit soil mineral ratios (N, P, K) along with target crop type to obtain fertilizer recommendations. Authenticated recommendation results SHALL be saved to the user's recommendation history.

#### Scenario: Requesting Fertilizer Recommendations
- **WHEN** a user submits N, P, K levels and target crop type
- **THEN** the system SHALL process the values through the ML logic and return recommended fertilizer types and application guidelines

#### Scenario: Authenticated fertilizer recommendation history saved
- **WHEN** an authenticated user receives a fertilizer recommendation
- **THEN** the system SHALL save the request and result in recommendation history
