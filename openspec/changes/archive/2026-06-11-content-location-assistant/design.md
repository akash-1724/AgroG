## Context

AgroGuide is adding user-support features: Educational Resources (for farmer crop-education and visitor guides), Location-Aware Farmer Discovery (to connect buyers with nearby local farmers), and an AI Agriculture Assistant (for advisory farm question-answering). This design specifies the database schemas, API routes, security boundaries, and frontend screens required.

## Goals / Non-Goals

**Goals:**
- Implement Educational Resource CRUD for Admins, and read-only catalog browsing with filtering for Farmers and Customers.
- Implement Farmer Location storage and nearby search using the Haversine distance formula, protecting location privacy.
- Implement an AI Assistant chat endpoint that supports OpenAI/Gemini providers via environment keys, falling back to a safe simulated mock response if keys are missing.
- Define DB schema migrations and RBAC filters on the backend and frontend.

**Non-Goals:**
- Installing PostGIS or other heavy geographic extensions (simple math-based Haversine calculation on latitude and longitude is sufficient).
- Implementing complex AI conversation management/vector databases.
- Creating an analytics dashboard.

## Decisions

### 1. Database Schema Design

We will add the following entities:

#### EducationalResource
- `id`: UUID (Primary Key)
- `title`: String(255), Not Null
- `slug`: String(255), Unique, Not Null
- `summary`: Text, Not Null
- `content`: Text (supports Markdown), Not Null
- `category`: String(100), Not Null
- `tags`: JSON/Array of Strings (e.g., tags list)
- `crop_tags`: JSON/Array of Strings
- `media_url`: String(500), Nullable
- `language`: String(10), Default "en"
- `status`: String(20) (e.g., "draft" | "published")
- `author_id`: UUID, Foreign Key to `users.id`
- `created_at`: DateTime, Default timezone.utc
- `updated_at`: DateTime, Default timezone.utc

#### FarmerLocation
- `id`: UUID (Primary Key)
- `farmer_id`: UUID, Unique, Foreign Key to `users.id`
- `latitude`: Float, Not Null
- `longitude`: Float, Not Null
- `address`: String(500), Nullable
- `district`: String(100), Nullable
- `city`: String(100), Nullable
- `state`: String(100), Nullable
- `location_visibility`: Boolean, Default True
- `updated_at`: DateTime, Default timezone.utc

#### AssistantConversation
- `id`: UUID (Primary Key)
- `user_id`: UUID, Nullable, Foreign Key to `users.id`
- `created_at`: DateTime, Default timezone.utc

#### AssistantMessage
- `id`: UUID (Primary Key)
- `conversation_id`: UUID, Foreign Key to `assistant_conversations.id`
- `role`: String(20) ("user" | "assistant")
- `content`: Text, Not Null
- `created_at`: DateTime, Default timezone.utc

---

### 2. Location-Aware Haversine Formula

To calculate distances between coordinates $(lat_1, lon_1)$ and $(lat_2, lon_2)$ without PostGIS:
$$\Delta lat = lat_2 - lat_1$$
$$\Delta lon = lon_2 - lon_1$$
$$a = \sin^2(\Delta lat/2) + \cos(lat_1) \cdot \cos(lat_2) \cdot \sin^2(\Delta lon/2)$$
$$c = 2 \cdot \text{atan2}(\sqrt{a}, \sqrt{1-a})$$
$$d = R \cdot c$$ (where $R = 6371\text{ km}$)

*Alternatives Considered*: Using sqlite spatialite / postgres postgis. Rejected to prevent complex binary dependency installation issues in development/CI.

### 3. Location Privacy Rule

To prevent exposing exact GPS coordinates:
- The backend nearby discovery endpoint (`GET /api/v1/farmers/nearby`) returns:
  - `distance_km`: Proximity.
  - `address`, `district`, `city`, `state`.
  - Rounded `latitude` and `longitude` (precision truncated to 2 decimal places, giving a ~1.1km blur radius) instead of exact raw coordinates.
- Raw exact coordinates are only returned on `GET /api/v1/farmers/me/location` to the owner farmer themselves.

### 4. AI Assistant Configurable Key and Safety Fallback

- The assistant reads env variables: `AI_PROVIDER` (e.g. `gemini` | `openai` | `fallback`), `GEMINI_API_KEY`, `OPENAI_API_KEY`.
- If no key is set or `AI_PROVIDER` is `fallback`, a rule-based advisor triggers local heuristic templates answering questions (e.g., about planting, soil preparation, pest disclaimers) with an amber warning banner.
- All AI responses append a rigid safety disclaimer warning against dangerous chemical dosages, legal guidance, or direct financial forecasts.

---

### 5. RBAC and Ownership Matrix

| Endpoint | Access Role | Ownership/Privacy Enforcement |
| --- | --- | --- |
| `GET /api/v1/educational/resources` | Anonymous | Filters out `draft` resources unless user is `Admin` |
| `POST/PATCH/DELETE /api/v1/educational/resources` | Admin | Strict `role == Admin` check |
| `PATCH /api/v1/farmers/me/location` | Farmer | Authenticated user is mapped directly to `farmer_id` |
| `GET /api/v1/farmers/nearby` | Anonymous | Filters out locations where `location_visibility` is false |
| `POST /api/v1/assistant/chat` | Authenticated | Asserts authentication (guest queries optional/disabled) |

---

### 6. Frontend Routes and Components Plan

- `/resources`: Public list of published articles with category tabs, tag filters, language selectors, and search input.
- `/resources/[slug]`: Markdown viewer parsing content, displaying crop tags, category, and author.
- `/admin/resources`: Data table displaying list of all resources, status badges, and edit/delete actions.
- `/admin/resources/new` and `/admin/resources/[id]/edit`: Form using React Hook Form, Zod schema validation, Category selects, Markdown editor text-area, draft/published status switch.
- `/nearby-farmers`: List card grid detailing nearby visible farmers, address/city, distance, and contact details, featuring a map placeholder or list sorting.
- `/farmer/location`: Settings page for farmers to update coordinates (via a simple coordinate picker or lookup), address details, and location visibility.
- `/assistant`: Interactive chat window displaying streaming text response bubbles, demo mode alert banner, and strict safety notes.

## Risks / Trade-offs

- **Risk** -> Farmers update their location with inaccurate arbitrary strings or coords.
  - **Mitigation** -> Validate coordinates ranges: Lat (-90 to 90) and Long (-180 to 180) inside backend pydantic schemes.
- **Risk** -> AI key failures blocking the assistant page.
  - **Mitigation** -> Gracefully catch external HTTP client exceptions and trigger the rule-based fallback response, logging errors internally without crashing.
