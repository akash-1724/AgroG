# Location-Aware Farmer Discovery Specification

## Purpose
Initial definition of the Location-Aware Farmer Discovery capability for AgroGuide.
## Requirements
### Requirement: Location-Based Farmer Discovery
The system SHALL allow users (customers and guest visitors) to search for active Farmers within a specific radius of geo-coordinates.
The system SHALL calculate distances using the Haversine formula on latitude/longitude coordinates and return active, visible farmers sorted by proximity.
To preserve farmer privacy, the backend SHALL return approximate location details (address, district/city/state, or coordinate approximations) to customers instead of raw exact farm coordinates.

#### Scenario: Searching for Farmers Nearby
- **WHEN** a customer provides latitude, longitude, and an optional search radius
- **THEN** the system SHALL calculate distances using a Haversine formula, return active farmers whose location_visibility is true, sorted by proximity, and omit raw exact latitude/longitude coordinates from the customer payload

### Requirement: Farmer Location Settings and Privacy
The system SHALL allow farmers to create, update, and manage their location profiles containing farmer_id, latitude, longitude, address, district/city/state, location_visibility, and updated_at.
The backend SHALL enforce ownership checks on location updates.
If a farmer sets location_visibility to false, their location data SHALL NOT be returned in nearby farmer searches by customers.

#### Scenario: Farmer Updates Own Location
- **WHEN** a farmer submits a location update with latitude, longitude, address, and visibility
- **THEN** the system SHALL validate the coordinates, save the record, and associate it with the authenticated farmer

#### Scenario: Non-owner Farmer Update Rejected
- **WHEN** a user attempts to update another farmer's location profile
- **THEN** the system SHALL reject the request with a 403 Forbidden error

