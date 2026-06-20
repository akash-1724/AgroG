## ADDED Requirements

### Requirement: Public Farmer Profile
The system SHALL expose a public farmer profile view for each Farmer. The profile SHALL include farm name, farmer name, approximate address/location, description, computed rating summary, review count, review summary, and active listings/produce.

#### Scenario: View public farmer profile
- **WHEN** a public user opens a valid Farmer profile page
- **THEN** the system SHALL show the Farmer's public farm details, approximate location, active listings, rating average, review count, and recent reviews

#### Scenario: Hidden exact coordinates
- **WHEN** a public user views a Farmer profile
- **THEN** the system SHALL NOT expose sensitive exact latitude and longitude values unless explicitly designed as public approximate data

### Requirement: Farmer Active Listings on Profile
The system SHALL show only active marketplace listings on public Farmer profile pages. Inactive and sold-out listings SHALL be hidden from public profile listing sections unless existing marketplace behavior intentionally exposes them through admin-only views.

#### Scenario: Profile shows active produce
- **WHEN** a Farmer has active and inactive listings
- **THEN** the public profile SHALL list active listings and omit inactive listings

### Requirement: Farmer Profile Editing
The system SHALL allow authenticated Farmers to update their own public profile fields, including farm name, address/location text, city/state/district where supported, description, and location visibility. Farmers SHALL NOT edit another Farmer's profile.

#### Scenario: Farmer edits own profile
- **WHEN** an authenticated Farmer submits valid updates for their own profile
- **THEN** the system SHALL save the profile fields and return the updated profile

#### Scenario: Farmer cannot edit another profile
- **WHEN** a Farmer attempts to update a different Farmer's profile
- **THEN** the system SHALL reject the request with a forbidden response

### Requirement: Profile Links from Marketplace
Marketplace listing cards and listing detail pages SHALL link to the listing Farmer's public profile when farmer information is available.

#### Scenario: Listing card links farmer profile
- **WHEN** a user views a marketplace listing card with farmer data
- **THEN** the UI SHALL provide a link to `/farmers/{farmer_id}`
