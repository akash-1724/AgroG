## ADDED Requirements

### Requirement: Article and Resource Browsing
The system SHALL display categorized educational guides, articles, and tutorials related to sustainable farming, crop management, and pest control.

#### Scenario: User Browses Educational Guides
- **WHEN** any user requests the educational library
- **THEN** the system SHALL return a list of educational articles filtered by category and tags

### Requirement: Educational Content Management
The system SHALL allow Admins to create, edit, and delete educational resources.

#### Scenario: Admin Publishes a Tutorial
- **WHEN** an authenticated Admin submits a new tutorial with title, category, and markdown content
- **THEN** the system SHALL create the resource and make it available in the public catalog
