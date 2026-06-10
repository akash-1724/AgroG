## Why

Currently, small and medium-scale farmers lack an integrated, modern platform that combines marketplace access, agricultural ML intelligence (crop and fertilizer recommendations, disease detection), educational resources, localized discovery, and an AI-powered conversational assistant. AgroGuide aims to bridge this gap by providing a production-grade AgriTech platform. 

Establishing the initial planning and specification foundation (Phase 0) is necessary to outline module boundaries, tech stack integration, data models, API boundaries, and deployment patterns before writing application code. Doing so ensures a decoupled, scalable monorepo structure, avoids security pitfalls, and mitigates architectural risks early.

## What Changes

This change is purely a planning and design phase (Phase 0) that creates the specs, design, and roadmap. It does not introduce any application code or framework initializations.

Specifically, it establishes:
- The modular monorepo folder structure (Next.js frontend + FastAPI backend + ML services).
- Module boundaries, database entity plan, and API boundaries.
- Auth and role-based access control (RBAC) schemas.
- Machine Learning service integration design.
- The incremental Phase 1 implementation checklist.

## Capabilities

### New Capabilities
- `auth-and-rbac`: User registration, authentication via JWT access/refresh tokens, Google OAuth, and Role-Based Access Control (Farmer, Customer, Admin).
- `farmer-marketplace`: Marketplace listings, inventory management, order placement, and transaction tracking.
- `crop-recommendation`: Soil- and weather-aware ML recommendation system (using N, P, K, pH, rainfall, etc.).
- `fertilizer-recommendation`: ML recommendation engine advising on fertilizer types based on soil parameters and crop targets.
- `plant-disease-detection`: Image upload and ML analysis to identify crop foliage diseases and suggest remedies.
- `educational-resources`: Content management system and catalog for agricultural guides, tips, and tutorials.
- `location-aware-farmer-discovery`: Geographic-based listing and discovery of nearby farmers.
- `ai-agriculture-assistant`: LLM-powered natural language conversational assistant for farming guidance.
- `analytics-dashboard`: Business and agricultural dashboard presenting sales, crop health, and system analytics.

### Modified Capabilities
<!-- None in this initial phase -->

## Impact

- **Codebase Structure**: Establishes a monorepo root structure (`/frontend` for Next.js, `/backend` for FastAPI, `/ml` for models and training pipelines, `/docker` for orchestration).
- **Security & Infrastructure**: Defines standard env templates, avoiding hardcoded secrets, mapping Redis caching, PostgreSQL migration schemas, Sentry monitoring, and GitHub Actions CI/CD workflows.
- **APIs and Services**: Defines boundaries between the FastAPI backend service, ML pipelines, and Next.js frontend clients.
