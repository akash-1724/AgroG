## ADDED Requirements

### Requirement: Crop Price Records
The system SHALL store crop price records with crop name, market name, district or state, min price, max price, modal price, unit, recorded date, source, and sample/demo status.

#### Scenario: Sample price record is stored
- **WHEN** seeded or imported sample price data is saved
- **THEN** each record SHALL include source metadata and `is_sample=true`

### Requirement: Price Trend Query API
The system SHALL expose crop price trend APIs that return available price records filtered by crop, market, state, and days where supported.

#### Scenario: Price trend data exists
- **WHEN** a client requests price trends for a crop with available records
- **THEN** the system SHALL return ordered trend data including price values, unit, market, state, recorded date, source, and sample/demo status

#### Scenario: Price trend data unavailable
- **WHEN** a client requests price trends for a crop with no available records
- **THEN** the system SHALL return an empty or unavailable state without inventing market prices

### Requirement: Crop Price Catalog
The system SHALL expose a list of crops for which price records are available.

#### Scenario: Crop catalog requested
- **WHEN** a client requests available price crops
- **THEN** the system SHALL return distinct crop names and enough metadata for frontend navigation

### Requirement: Price Data Honesty
The backend and frontend SHALL clearly distinguish sample/demo price data from live/imported price data and SHALL NOT present sample data as live market data.

#### Scenario: Sample data displayed
- **WHEN** price trend data contains sample/demo records
- **THEN** the frontend SHALL show a visible sample/demo data label or disclaimer

#### Scenario: Live provider unavailable
- **WHEN** a configured live or external price provider is unavailable
- **THEN** the system SHALL return a controlled unavailable state or sample-labeled fallback, not fabricated live prices

### Requirement: Price Trend Frontend
The system SHALL provide frontend price pages for browsing crop price trends and viewing focused crop trend details.

#### Scenario: User views price trends
- **WHEN** a user opens `/prices`
- **THEN** the UI SHALL show available crops, trend summaries, source labels, and sample/demo disclaimers where applicable

#### Scenario: User views crop price detail
- **WHEN** a user opens `/prices/{crop}` for a crop with data
- **THEN** the UI SHALL show trend records for that crop with market, state, price values, unit, dates, and source/sample status
