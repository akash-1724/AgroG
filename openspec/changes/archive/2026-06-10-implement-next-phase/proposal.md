## Why

Having completed Phase 0 (base monorepo workspace scaffolding, SQLAlchemy data model mappings, async database integration, authentication API routers, and ML inference service endpoints), we are ready to proceed with implementing the core features and user interfaces of the AgroGuide platform (Phase 1). This change covers the implementation of the marketplace checkout, geo-proximity searches, AI chatbot streaming, and Next.js frontend pages.

## What Changes

This change implements the full feature checklist defined in the project roadmap, including:
- **Backend Features**: Marketplace listings CRUD, shopping cart checkout, order status flow, geo-queries for localized farmer search, and streaming LLM assistant gateway.
- **Frontend App**: Next.js App Router workspace client, styling configurations, shadcn/ui library, global authentication context, state query wrappers.
- **Frontend Feature Views**: Authentication forms, crop marketplace listing/purchasing, diagnostic recommendation forms, plant disease upload, and user role-specific dashboards (Farmer, Customer, Admin).
- **Deployment configs**: Root `docker-compose.yml`, multi-stage Dockerfiles, GitHub Actions workflow, and Sentry monitoring integrations.

## Capabilities

### New Capabilities
<!-- None. Features are implemented using the specifications already defined and synced. -->

### Modified Capabilities
<!-- None. Spec-level requirements remain unchanged. -->

## Impact

- **Backend**: Implements the business logic endpoints defined in the spec-driven architecture under `/backend/app/api/v1/endpoints/`.
- **Frontend**: Bootstraps the visual layout and user interactions in `/frontend/src/`.
- **DevOps**: Introduces dockerized service configurations and root execution compose pipelines.
