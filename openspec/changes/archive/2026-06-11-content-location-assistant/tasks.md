## 1. Database Schema Migrations

- [x] 1.1 Create database model definitions in `backend/app/models/` for `EducationalResource`, `FarmerLocation`, `AssistantConversation`, and `AssistantMessage`.
- [x] 1.2 Generate and run alembic/SQL migration script to create the tables.
- [x] 1.3 Add backend API Pydantic schemas in `backend/app/schemas/` for resources, locations, and assistant payloads.

## 2. Educational Resources Backend APIs

- [x] 2.1 Implement resource routes in `backend/app/api/v1/endpoints/educational.py` supporting resource CRUD.
- [x] 2.2 Add role-based RBAC filters to endpoints: restrict create, update, and delete to `Admin` role.
- [x] 2.3 Add slug validation, search parameters (title, category, tags, crop tags, language) and visibility filtering (hide `draft` from non-admins).
- [x] 2.4 Register the router in `backend/app/api/v1/api.py`.

## 3. Location-Aware Farmer Discovery Backend APIs

- [x] 3.1 Implement location endpoints in `backend/app/api/v1/endpoints/farmers.py`.
- [x] 3.2 Add `PATCH /farmers/me/location` to allow farmers to manage their coordinates, address, and visibility.
- [x] 3.3 Add `GET /farmers/nearby` implementing the math-based Haversine calculation to filter and sort visible farmers within an input radius.
- [x] 3.4 Ensure the nearby endpoint suppresses exact latitude/longitude, rounding coordinates to 2 decimal places to maintain privacy.

## 4. AI Agriculture Assistant Backend APIs

- [x] 4.1 Create helper service in `backend/app/services/assistant.py` or inside ML service to load environment AI provider API keys.
- [x] 4.2 Add safety filtration checks to intercept prompts asking for dangerous chemical dosage or financial projections.
- [x] 4.3 Implement `POST /api/v1/assistant/chat` endpoint to return conversational answers, appending disclaimers and provider metadata.
- [x] 4.4 Implement conversational history endpoints `GET /api/v1/assistant/conversations` (optional/simple storage).

## 5. Educational Resources Frontend Interface

- [x] 5.1 Create public library view at `frontend/src/app/resources/page.tsx` with filtering (search, categories, tags) and grid cards.
- [x] 5.2 Create resource detail viewer at `frontend/src/app/resources/[slug]/page.tsx` rendering markdown articles.
- [x] 5.3 Implement Admin dashboard page at `frontend/src/app/admin/resources/page.tsx` displaying the complete list of articles (published and drafts).
- [x] 5.4 Build creation/editing form views at `frontend/src/app/admin/resources/new/page.tsx` and `frontend/src/app/admin/resources/[id]/edit/page.tsx`.

## 6. Nearby Farmers & Location Setting Frontend Interface

- [x] 6.1 Implement the farmer location form at `frontend/src/app/farmer/location/page.tsx` supporting address, coordinates input, and visibility options.
- [x] 6.2 Implement nearby discovery grid page at `frontend/src/app/nearby-farmers/page.tsx` showing active farmers sorted by distance.

## 7. AI Assistant Chat Frontend Interface

- [x] 7.1 Implement interactive chat assistant interface at `frontend/src/app/assistant/page.tsx`.
- [x] 7.2 Include user/role context headers, fallback warnings when provider keys are missing, and safety/disclaimer warnings.

## 8. Verification & Integration Testing

- [x] 8.1 Write backend unit/integration tests covering location distance checks, privacy coordinate blurring, and resource RBAC.
- [x] 8.2 Verify Next.js build passes with no compilation or TypeScript errors.
