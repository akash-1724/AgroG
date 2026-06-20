## ADDED Requirements

### Requirement: Eligible Customer Review Creation
The system SHALL allow Customers to create reviews with rating 1-5 and comment only for listings or farmers connected to their completed purchases. Farmers SHALL NOT review themselves or their own listings.

#### Scenario: Customer reviews completed purchase
- **WHEN** a Customer submits a review for a completed order item they purchased
- **THEN** the system SHALL create the review with customer, farmer, listing, order, rating, comment, and timestamps

#### Scenario: Review before completed purchase blocked
- **WHEN** a Customer submits a review for a listing or Farmer without an eligible completed order item
- **THEN** the system SHALL reject the review request

#### Scenario: Farmer self-review blocked
- **WHEN** a Farmer attempts to review their own Farmer profile or own listing
- **THEN** the system SHALL reject the review request

### Requirement: Duplicate Review Prevention
The system SHALL prevent a Customer from repeatedly reviewing the same purchased order item/listing combination. Duplicate prevention SHALL be enforced by application validation and, where practical, by database uniqueness constraints or indexes.

#### Scenario: Duplicate purchased item review blocked
- **WHEN** a Customer has already reviewed a completed order item and submits another review for the same item/listing
- **THEN** the system SHALL reject the duplicate review request

### Requirement: Review Visibility and Moderation
The system SHALL expose public review lists for Farmer profiles and listings. Admins SHALL be able to delete reviews for moderation. Farmers SHALL be able to view reviews about them but SHALL NOT modify those reviews.

#### Scenario: Public farmer reviews listed
- **WHEN** a public user requests reviews for a Farmer
- **THEN** the system SHALL return visible reviews for that Farmer with rating, comment, reviewer display data where safe, and timestamps

#### Scenario: Public listing reviews listed
- **WHEN** a public user requests reviews for a listing
- **THEN** the system SHALL return visible reviews for that listing with rating, comment, reviewer display data where safe, and timestamps

#### Scenario: Admin deletes review
- **WHEN** an Admin deletes a review
- **THEN** the system SHALL remove or moderate the review and update computed rating summaries accordingly

### Requirement: Derived Rating Summaries
The system SHALL compute Farmer and listing rating summaries from review records. Public profile pages, listing cards, and listing detail pages SHALL display rating average and review count when reviews exist.

#### Scenario: Rating summary computed from reviews
- **WHEN** reviews exist for a Farmer or listing
- **THEN** the system SHALL compute average rating and review count from review records rather than relying on manually edited rating values

#### Scenario: No reviews fallback
- **WHEN** no reviews exist for a Farmer or listing
- **THEN** the system SHALL display an unrated or zero-review state without fabricating a rating
