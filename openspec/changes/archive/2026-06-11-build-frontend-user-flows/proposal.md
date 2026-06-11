## Why

The backend of AgroGuide has been established with core authentication, role-based access control, marketplace listings, and order workflows. However, the user interface currently consists of a default Next.js starter page and lacks the interactive screens needed for farmers and customers to leverage these capabilities. Providing user-facing flows is now critical to make the application functional, allowing users to register, log in, manage listings, browse the marketplace, and track orders.

## What Changes

This change introduces the core web frontend user interface and API client integration using Next.js (App Router), TypeScript, and Tailwind CSS. The following capabilities will be implemented:
- Replace the Next.js landing page with a tailored, responsive AgroGuide landing/home page.
- Build auth pages: login, role-specific registration (Customer/Farmer), session logic, and secure client-side storage of access tokens.
- Add marketplace pages to browse crop/product listings with sorting, searching, pagination, and detail pages.
- Add farmer-specific flows to list crops, update listings, view marketplace orders, and update order statuses.
- Add customer-specific flows to place orders, view order history, and manage accounts.
- Establish the frontend foundation: Axios/fetch typed API wrapper, protected routes, TanStack Query integration, and Zod/React-Hook-Form validations.

## Capabilities

### New Capabilities
- `frontend-user-flows`: UI representation and end-to-end integration of user registration, authentication, crop listing management, marketplace browsing, and order tracking.

### Modified Capabilities
<!-- None. We are not modifying backend specs. -->

## Impact

- **Frontend**: Adds Next.js pages, routing, global state, forms, API integration layer, and navigation.
- **Backend API**: The frontend will communicate with existing backend endpoints (auth, users, crop-listings, orders).
- **ML Services**: Out of scope for this phase.
- **Deployment**: Local docker-compose configuration or local development runs are used; full production deployment setup remains deferred.
