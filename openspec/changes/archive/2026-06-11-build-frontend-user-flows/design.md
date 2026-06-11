## Context

AgroGuide consists of a Next.js frontend and a FastAPI backend with PostgreSQL. The backend services have functional REST endpoints for user authentication, registration, crop listings, and orders, along with RBAC middleware distinguishing `farmer`, `customer`, and `admin` roles. Currently, the frontend is a boilerplate Next.js setup and does not interface with the backend. This change designs and establishes the React component structure, routing paths, state handling, and integration layer required for user-facing flows.

## Goals / Non-Goals

**Goals:**
- Set up a clean, production-grade directory structure inside `frontend/` using Next.js App Router and TypeScript.
- Define a central API client (using Axios or native fetch wrapper) that reads backend base URL from environment variables, handles JWT injection, and catches 401/403 errors.
- Build clean, functional, and visually premium pages for authentication, marketplace browsing/searching, farmer listing management, and order workflows.
- Integrate TanStack Query for caching and server-state synchronization.
- Implement forms with validation using React Hook Form and Zod.
- Block/redirect unauthenticated users or users with incorrect roles using standard React context + Next.js router guards.

**Non-Goals:**
- No ML diagnostic features or pages (e.g. crop recommendation UI, plant disease detection UI).
- No AI agricultural assistant or chat pages.
- No full analytics dashboard implementation.
- No production deployment configs (Docker Compose local dev is sufficient).
- No mock payment gateway UI integration (submitting the order directly creates a pending order).

## Decisions

### 1. Routing Structure
We will map out the frontend routes cleanly using Next.js App Router:
- `/` -> Landing/Home page with high-quality visual call-to-actions.
- `/login` -> Email/Password login page.
- `/register` -> Combined register flow (selecting role toggle `farmer` vs `customer` to dynamically show farmer profile/farm info fields).
- `/marketplace` -> Search, filter, and pagination listing page.
- `/marketplace/[id]` -> Details and checkout/ordering shell.
- `/orders` -> Customer order history page.
- `/farmer/listings` -> List of active/inactive crops created by the current farmer.
- `/farmer/listings/new` -> Crop listing creation form (Zod validated).
- `/farmer/listings/[id]/edit` -> Crop listing edit form.
- `/farmer/orders` -> Incoming orders list for the farmer, with status action buttons.
- `/account` -> Profile page to view user data/role.

*Alternatives Considered*: Placing customer orders and farmer orders under the same page path. However, splitting them preserves RBAC isolation in code.

### 2. Session and Authentication Management
- Session token (JWT access token) will be stored in `localStorage` or a secure `Cookie` (client-side read).
- Provide a `AuthContext` to expose `currentUser`, `isAuthenticated`, `role`, `loading`, and helper functions (`login()`, `logout()`, `register()`).
- High-level layout wrappers or client-side middleware redirects will guard `/farmer/*` routes to check for `role === 'farmer'` and general protected paths.

### 3. API Integration Layer
- A customized wrapper using `axios` will be configured inside `frontend/src/lib/api-client.ts`.
- Automatically reads `NEXT_PUBLIC_API_URL` environment variable.
- Injects `Authorization: Bearer <token>` automatically if present in the client storage.
- Intercepts 401 Unauthorized errors to automatically purge local session and redirect to `/login`.

## Risks / Trade-offs

- **Risk**: Dynamic client-side layout checks causing content flash (FOUC / layout shift) while loading session.
  - **Mitigation**: Add a global skeleton loader state or a simple auth-checking spinner in `AuthContext` before rendering sub-routes.
- **Risk**: Backend updates could conflict with typed schemas.
  - **Mitigation**: Define clean TS interfaces matching backend model serialization models.
