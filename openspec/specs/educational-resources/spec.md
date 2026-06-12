# Educational Resources Specification

## Purpose
Initial definition of the Educational Resources capability for AgroGuide.
## Requirements
### Requirement: Article and Resource Browsing
The system SHALL display categorized educational guides, articles, and tutorials related to sustainable farming, crop management, and pest control.
Farmers and customers SHALL be able to browse published resources, but draft resources MUST only be visible to Admins.
The system SHALL support searching and filtering resources by title, category, tags, crop tags, and language.

#### Scenario: User Browses Educational Guides
- **WHEN** any farmer or customer requests the educational library
- **THEN** the system SHALL return a list of published educational articles filtered by title search, category, language, and tags, excluding any draft resources

#### Scenario: Admin Browses All Guides
- **WHEN** an Admin requests the educational library
- **THEN** the system SHALL return all educational articles including both published and draft resources

### Requirement: Educational Content Management
The system SHALL allow Admins to create, edit, publish, unpublish, and delete educational resources.
Educational resource fields SHALL include ID, title, slug, summary, content, category, tags, crop_tags, media_url, language, draft/published status, author_id, created_at, and updated_at.

#### Scenario: Admin Publishes a Tutorial
- **WHEN** an authenticated Admin submits a new tutorial with title, category, status "published", and content
- **THEN** the system SHALL create the resource and make it available in the public catalog

#### Scenario: Admin Creates a Draft
- **WHEN** an authenticated Admin submits a new resource with status "draft"
- **THEN** the system SHALL create the resource but hide it from the public catalog

