## MODIFIED Requirements

### Requirement: Plant Leaf Image Analysis
The system SHALL allow users to upload images of plant leaves to identify disease types.
The system SHALL validate the upload parameters:
- Enforce file format checks: only allow `image/jpeg`, `image/png`, and `image/jpg` content types.
- Enforce file size checks: limit uploads to a maximum of 5MB.
- Return a `model_status: "demo"` flag and an advisory disclaimer statement in the payload warning that baseline diagnosis heuristics are for simulation purposes and not agronomic certainty.

#### Scenario: Analyzing a Foliage Image
- **WHEN** a user uploads a valid image of a plant leaf (PNG/JPEG under 5MB)
- **THEN** the system SHALL run the classification logic and return the predicted disease status, confidence level, remedy, `model_status: "demo"`, and an advisory disclaimer

#### Scenario: Submitting Invalid File Format
- **WHEN** a user uploads an invalid file format (e.g. PDF or plain text)
- **THEN** the system SHALL reject the upload and return a 400 Bad Request error code

#### Scenario: Submitting Oversized Leaf Image
- **WHEN** a user uploads an image larger than 5MB
- **THEN** the system SHALL reject the upload and return a 413 Payload Too Large error code
