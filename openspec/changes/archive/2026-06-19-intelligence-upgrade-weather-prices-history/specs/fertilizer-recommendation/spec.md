## MODIFIED Requirements

### Requirement: Fertilizer Recommendation Prediction
The system SHALL allow users to submit soil, crop, and nutrient input data to receive a fertilizer recommendation from the ML service. Authenticated recommendation results SHALL be saved to the user's recommendation history.

#### Scenario: Successful fertilizer recommendation
- **WHEN** a user submits valid fertilizer recommendation inputs
- **THEN** the system SHALL return a fertilizer recommendation and model/provider status

#### Scenario: Authenticated fertilizer recommendation history saved
- **WHEN** an authenticated user receives a fertilizer recommendation
- **THEN** the system SHALL save the request and result in recommendation history
