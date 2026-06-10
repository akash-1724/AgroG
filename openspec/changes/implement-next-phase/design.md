## Context

This design document establishes the implementation blueprint for the Next Phase of the AgroGuide project. The goal of this phase is to move from the structural foundations established in Phase 0 to functional feature sets across the backend, frontend, and deployment layers.

---

## Goals / Non-Goals

**Goals:**
- **Feature Completion**: Implement the remaining backend endpoints (Marketplace checkout, Geo-search, AI Assistant streaming).
- **Frontend Visual & UX Setup**: Scaffold the Next.js App Router layout, install Tailwind/shadcn component libraries, and construct operational pages/dashboards.
- **Orchestration**: Create Docker files and root `docker-compose.yml` to run the entire system.

**Non-Goals:**
- **Infrastructure Provisioning**: Cloud server hosting setups, SSL certificates, or domain registries are out of scope.

---

## Decisions

### 1. Backend Marketplace & Geo-Queries
- **Marketplace Orders**: Implement database checkout logic in `app/api/v1/endpoints/marketplace.py`. Concurrency on available crop stock is managed via transactional SQL updates.
- **Proximity Search**: Geolocation search inside `app/api/v1/endpoints/farmers.py` calculates distance in meters using the Haversine formula directly in PostgreSQL queries using indexed latitude and longitude float values.

### 2. AI Assistant Streaming
- The assistant endpoint `/assistant/chat` leverages standard Server-Sent Events (SSE) using FastAPI's `StreamingResponse` to stream token outputs from the LLM client (Gemini/OpenAI) to the browser client in real time.

### 3. Frontend & Styling
- **CSS System**: Vanilla Tailwind CSS with custom font and harmonious HSL color system extensions inside `tailwind.config.js`.
- **UI Components**: Bootstrap reusable components using `shadcn/ui` (built on Radix Primitives and Lucide React icons) for forms, dashboards, and tables.
- **Forms**: React Hook Form with Zod integration to ensure runtime and design-time schema validation of input data.

### 4. Dockerization
- Individual multi-stage Dockerfiles will be created for each package folder (`/backend`, `/frontend`, `/ml_service`).
- A root-level `docker-compose.yml` will bind them together, mounting PostgreSQL and Redis containers with persistent volume mounts.

---

## Risks / Trade-offs

- **[Risk] High Latency on Haversine Geo-Search** → *Mitigation*: Limit maximum search radius to 50km and ensure the DB query filters by bounding boxes using index ranges before calculating exact trigonometric distances.
- **[Risk] LLM Cost / Spamming** → *Mitigation*: Restrict streaming assistant access to authenticated users only and enforce a simple token rate-limiting bucket.
