## Why

AgroGuide lacks key user-support modules to assist farmers with localized crop-selling visibility, educational support, and basic advisory question-answering. This proposal introduces Educational Resources, Location-Aware Farmer Discovery, and an AI Agriculture Assistant to complete these interactive capabilities.

## What Changes

- Add **Educational Resources** endpoint, admin panel, and visitor list/detail views with category/tag filtering and draft/published status.
- Add **Location-Aware Farmer Discovery** with approximate geolocations, privacy control visibility, and proximity calculations on the backend using the Haversine formula.
- Add an **AI Agriculture Assistant** with conversational chat endpoints, structured safety instructions, and a local mock fallback when AI provider API keys are missing.
- Define DB schema migrations for resources, locations, and assistant logs.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `educational-resources`: Expands to support drafts, media URLs, tags, crop tags, language, and admin-only write endpoints.
- `location-aware-farmer-discovery`: Introduces privacy filters, approximate coordinates suppression, state/city columns, and Haversine distance sorting.
- `ai-agriculture-assistant`: Introduces strict system disclaimers (e.g. chemical/safety warning exclusions), chat persistence options, and API key fallback behavior.

## Impact

- **Database**: Creates `EducationalResource`, `FarmerLocation`, `AssistantConversation`, and `AssistantMessage` tables.
- **Backend API**: Exposes `/api/v1/educational/resources`, `/api/v1/farmers/nearby`, `/api/v1/farmers/me/location`, and `/api/v1/assistant/chat` (and conversation history endpoints).
- **Frontend Pages**: Adds `/resources`, `/nearby-farmers`, `/farmer/location`, `/assistant`, and `/admin/resources` pages.
