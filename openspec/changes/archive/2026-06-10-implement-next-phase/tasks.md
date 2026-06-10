## 1. Backend Marketplace & Assistant Endpoints

- [x] 1.1 Implement `/marketplace` endpoints for Listing CRUD
- [x] 1.2 Implement `/marketplace/orders` endpoints for placing orders and updating statuses
- [x] 1.3 Implement geolocation queries in SQL to find Farmers within radius `/farmers/search`
- [x] 1.4 Implement `/assistant/chat` endpoint using streaming integration with LLM client
- [x] 1.5 Create article/tutorial CRUD endpoints for admins under `/educational`

## 2. Frontend Setup & UI System

- [x] 2.1 Install frontend dependencies (Tailwind, Lucide-react, TanStack Query, React Hook Form, Zod)
- [x] 2.2 Configure Tailwind colors and fonts to support rich theme aesthetics
- [x] 2.3 Bootstrap shadcn/ui components (Button, Input, Card, Dialog, Toast, Select)
- [x] 2.4 Implement base layouts, global state context for auth, and client fetch wrappers

## 3. Frontend Features & Dashboard Construction

- [x] 3.1 Implement Auth forms (Login, Register, Google login buttons) with React Hook Form and Zod
- [x] 3.2 Build Marketplace browsing grids, search filters, and detail view pages
- [x] 3.3 Build Recommendation forms (Crop metrics, Fertilizer selectors) and render diagnostic summaries
- [x] 3.4 Create Plant Disease picture upload area with diagnostic readout
- [x] 3.5 Build Farmer Dashboard (listing management, orders board) and Customer Dashboard (purchases tracker)
- [x] 3.6 Build Admin Dashboard (tutorials CMS editor)

## 4. Docker, DevOps & CI/CD

- [x] 4.1 Write root-level docker-compose.yml to run database, redis, backend, ml_service, and frontend
- [x] 4.2 Create custom Dockerfiles for backend, frontend, and ml_service
- [x] 4.3 Set up GitHub Actions CI workflow to run linters, types verification, and unit tests
- [x] 4.4 Add Sentry integration in frontend, backend, and ml_service configurations
