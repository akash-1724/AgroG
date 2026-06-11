## 1. Frontend Foundations & API Client

- [x] 1.1 Add required npm packages (axios, @tanstack/react-query, react-hook-form, zod) to `frontend/package.json` and install them.
- [x] 1.2 Replace the Next.js landing template in `frontend/src/app/page.tsx` with a responsive AgroGuide homepage.
- [x] 1.3 Create the layout and navigation components in `frontend/src/app/layout.tsx` (header, footers, responsive mobile menu drawer).
- [x] 1.4 Implement API Client wrapper `frontend/src/lib/api-client.ts` parsing `NEXT_PUBLIC_API_URL`, setting up authorization header injections and 401 response interceptors.

## 2. Authentication & Session State

- [x] 2.1 Implement `frontend/src/context/AuthContext.tsx` providing user details, authentication state, login, registration, and logout flows.
- [x] 2.2 Create `/login` page (`frontend/src/app/login/page.tsx`) with React Hook Form + Zod validation.
- [x] 2.3 Create `/register` page (`frontend/src/app/register/page.tsx`) supporting customer and farmer roles, dynamically displaying additional fields (e.g. farm name, description) for the farmer.
- [x] 2.4 Add client-side route protection wrappers or hooks (`frontend/src/components/ProtectedRoute.tsx`) to guard restricted paths like `/orders` and `/farmer/*`.

## 3. Marketplace browsing

- [x] 3.1 Create `/marketplace` page (`frontend/src/app/marketplace/page.tsx`) displaying active crop listings.
- [x] 3.2 Add search, category filters, sorting (price, date), and pagination controls on the marketplace page.
- [x] 3.3 Create `/marketplace/[id]` detail page (`frontend/src/app/marketplace/[id]/page.tsx`) showing listing metadata, farmer details, and an order placing form.

## 4. Farmer Listing and Order Management

- [x] 4.1 Create farmer dashboard shell and `/farmer/listings` page (`frontend/src/app/farmer/listings/page.tsx`) displaying listings managed by the logged-in farmer.
- [x] 4.2 Create `/farmer/listings/new` page (`frontend/src/app/farmer/listings/new/page.tsx`) containing a Zod-validated creation form.
- [x] 4.3 Create `/farmer/listings/[id]/edit` page (`frontend/src/app/farmer/listings/[id]/edit/page.tsx`) for modification.
- [x] 4.4 Create `/farmer/orders` page (`frontend/src/app/farmer/orders/page.tsx`) showing customer orders, with action buttons to update order status (e.g. Confirm, Ship, Deliver).

## 5. Customer Orders & Profiles

- [x] 5.1 Create `/orders` page (`frontend/src/app/orders/page.tsx`) allowing customers to view their current and historic order history.
- [x] 5.2 Create `/account` page (`frontend/src/app/account/page.tsx`) representing user details and logout options.

## 6. Verification and Error Handling

- [x] 6.1 Create reusable components for loading states, error boundaries, empty lists, and validation alert cards.
- [x] 6.2 Conduct manual checks and testing of auth flows, listing creation, and ordering flows as documented in the verification plan.
