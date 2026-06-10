## 1. Monorepo Initialization & Setup

- [x] 1.1 Initialize monorepo root structure and package.json workspaces config
- [x] 1.2 Setup gitignore, eslint, prettier, and env.example at root
- [x] 1.3 Create Next.js project inside `/frontend` directory
- [x] 1.4 Create FastAPI structure inside `/backend` directory
- [x] 1.5 Create ML service structure inside `/ml_service` directory

## 2. Backend Base & Database Setup

- [x] 2.1 Install backend dependencies (FastAPI, SQLAlchemy, Alembic, Pydantic, asyncpg, passlib, redis)
- [x] 2.2 Configure SQLAlchemy 2.0 async database session manager
- [x] 2.3 Initialize Alembic in the `/backend` directory and create base migration scripts
- [x] 2.4 Implement PostgreSQL schemas and models for User, FarmerProfile, CropListing, Order, OrderItem, and Logs
- [x] 2.5 Setup Redis cache helper functions inside core utilities

## 3. Auth, RBAC & Google OAuth

- [x] 3.1 Implement password hashing using bcrypt helper functions
- [x] 3.2 Implement JWT encoding, decoding, access and refresh token authentication middleware
- [x] 3.3 Create the `/auth/register` and `/auth/token` routes in FastAPI
- [x] 3.4 Create RoleChecker FastAPI dependency to guard admin and farmer routes
- [x] 3.5 Implement Google OAuth backend authentication handler `/auth/google`

## 4. ML Service (Scikit-Learn/XGBoost/FastAPI)

- [x] 4.1 Setup FastAPI wrapper, requirements, and dependencies in `/ml_service`
- [x] 4.2 Set up serialization and loading handlers for Crop Recommendation XGBoost and Fertilizer Recommendation models
- [x] 4.3 Implement ML FastAPI endpoints `/recommendations/crop` and `/recommendations/fertilizer`
- [x] 4.4 Set up PyTorch/TensorFlow/Scikit-Image placeholder classification pipelines for Plant Disease Detection
- [x] 4.5 Implement prediction endpoint `/disease/detect` in `ml_service`

## 5. Backend Marketplace, Geo-Query & Assistant Endpoints

- [ ] 5.1 Implement `/marketplace` endpoints for Listing CRUD (Farmer listing creation, public browsing)
- [ ] 5.2 Implement `/marketplace/orders` endpoints for placing orders and updating statuses
- [ ] 5.3 Implement geolocation queries in SQL using indices to find Farmers within radius `/farmers/search`
- [ ] 5.4 Implement `/assistant/chat` endpoint using streaming integration with the Gemini or OpenAI client
- [ ] 5.5 Create article/tutorial CRUD endpoints for admins under `/educational`

## 6. Frontend Setup & UI System

- [ ] 6.1 Install frontend dependencies (Tailwind, Lucide-react, TanStack Query, React Hook Form, Zod)
- [ ] 6.2 Configure Tailwind colors and fonts to support rich theme aesthetics
- [ ] 6.3 Bootstrap shadcn/ui components (Button, Input, Card, Dialog, Toast, Select)
- [ ] 6.4 Implement base layouts, global state context for auth, and client fetch wrappers using Axios/Fetch

## 7. Frontend Features & Dashboard Construction

- [ ] 7.1 Implement Auth forms (Login, Register, Google login buttons) with React Hook Form and Zod
- [ ] 7.2 Build Marketplace browsing grids, search filters, and detail view pages
- [ ] 7.3 Build Recommendation forms (Crop metrics, Fertilizer selectors) and render diagnostic summaries
- [ ] 7.4 Create Plant Disease picture upload area with diagnostic readout
- [ ] 7.5 Build Farmer Dashboard (listing management, orders board) and Customer Dashboard (purchases tracker)
- [ ] 7.6 Build Admin Dashboard (tutorials CMS editor)

## 8. Docker, DevOps & CI/CD

- [ ] 8.1 Write root-level `docker-compose.yml` to run database, redis, backend, ml_service, and frontend
- [ ] 8.2 Create custom Dockerfiles for backend, frontend, and ml_service
- [ ] 8.3 Set up GitHub Actions CI workflow to run linters, types verification, and unit tests
- [ ] 8.4 Add Sentry integration in frontend, backend, and ml_service configurations
