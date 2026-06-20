## MODIFIED Requirements

### Requirement: Plant Disease Detection
The system SHALL allow users to submit plant images for disease detection and return a disease result from the ML service or configured demo behavior. Authenticated detection results SHALL be saved to the user's recommendation history.

#### Scenario: Successful disease detection
- **WHEN** a user submits a valid plant image for disease detection
- **THEN** the system SHALL return a disease detection result and model/provider status

#### Scenario: Authenticated disease detection history saved
- **WHEN** an authenticated user receives a disease detection result
- **THEN** the system SHALL save the request metadata and result in recommendation history
