## 1. Database Models & Migrations

- [x] 1.1 Create the `RefreshToken` database model in `backend/app/models/` mapping token strings, users, expiration, and revocation flags
- [x] 1.2 Verify `User` and `FarmerProfile` SQLAlchemy models support proper constraints and relationships
- [x] 1.3 Generate and execute Alembic database migrations to apply the new `refresh_tokens` table

## 2. Core Authentication Endpoints

- [x] 2.1 Implement `POST /api/v1/auth/register` allowing `farmer` and `customer` signup, auto-creating a `FarmerProfile` for farmers, and blocking `admin` signup
- [x] 2.2 Implement `POST /api/v1/auth/login` generating short-lived access tokens and long-lived refresh tokens saved in the database
- [x] 2.3 Implement `POST /api/v1/auth/refresh` verifying token validity and refresh token database state to issue new access tokens
- [x] 2.4 Implement `POST /api/v1/auth/logout` lookup that marks the request refresh token as revoked in the database
- [x] 2.5 Implement `GET /api/v1/auth/me` returning full authenticated user model metadata

## 3. Authorization Routes & Verification

- [x] 3.1 Verify `RoleChecker` decorator logic blocks unauthorized access to role-protected endpoints
- [x] 3.2 Add role-protected verification routes `/api/v1/auth/farmer-only-test` and `/api/v1/auth/admin-only-test`
- [x] 3.3 Document manual testing commands in README and write test script validating registration, login, token refresh, role blocks, and logout/revocation flow
