# Location-Aware Farmer Discovery Specification

## Purpose
Initial definition of the Location-Aware Farmer Discovery capability for AgroGuide.

## Requirements

### Requirement: Location-Based Farmer Discovery
The system SHALL allow users to search for active Farmers within a specific radius of geo-coordinates.

#### Scenario: Searching for Farmers Nearby
- **WHEN** a user provides latitude, longitude, and an optional search radius
- **THEN** the system SHALL calculate distances using spatial queries and return a list of active Farmers within that radius sorted by proximity
