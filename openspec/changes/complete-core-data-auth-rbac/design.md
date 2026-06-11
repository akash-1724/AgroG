## Context

We need to establish a stable authentication and authorization foundation for AgroGuide before implementing full marketplace transacting and dashboards. This design defines database models, token lifecycle management, logout/revocation flows, and endpoints to verify security constraints.

## Goals / Non-Goals

**Goals:**
- Implement secure email/password auth using bcrypt.
- Implement database-persisted and revocable refresh tokens.
- Add dynamic role-based access control (RBAC) route dependencies in FastAPI.
- Block public creation of Admin roles via standard `/register` endpoint.
- Verify migration compatibility with SQLAlchemy 2.0 and Alembic.

**Non-Goals:**
- Implementing any Google OAuth flows (deferred).
- Developing frontend UI components or dashboards in this phase.
- Adding marketplace listing, shopping cart, or ML classification logic.

## Decisions

### 1. Database Schema Updates
- **`RefreshToken` table**:
  - `id`: UUID (Primary Key)
  - `user_id`: UUID (ForeignKey to `users.id` with cascade delete)
  - `token`: String(500) (uniquely indexed refresh token value)
  - `expires_at`: DateTime (expiration timestamp)
  - `is_revoked`: Boolean (default: False)
  - `created_at`: DateTime (default: current UTC timestamp)

### 2. Registration Restrictions
- **Farmer Profiles**: When a user registers with `role: "farmer"`, a corresponding `FarmerProfile` database row is initialized with empty fields to support listings.
- **Admin Lock**: The POST `/api/v1/auth/register` endpoint will reject registration payloads containing `role: "admin"` with `400 Bad Request`. Admin users must be seeded directly or registered via a secure command-line shell script.

### 3. Token Lifecycle & Revocation
- **Access Tokens**: Short-lived JWT (15 minutes), containing user ID, role, and full name.
- **Refresh Tokens**: Long-lived JWT (7 days), stored in the database.
- **Refresh Flow**: The `/api/v1/auth/refresh` endpoint expects `refresh_token` in request body. It verifies:
  1. Token signature and expiration date.
  2. Database lookup: token exists, `is_revoked = False`, and user exists.
  3. If valid, issues a new access token.
- **Logout Flow**: The `/api/v1/auth/logout` endpoint accepts the refresh token, looks it up in the database, and flags `is_revoked = True` to terminate session validity.

### 4. RBAC Mapping Matrix
| Route | Method | Permitted Roles | Description |
| :--- | :--- | :--- | :--- |
| `/api/v1/auth/register` | POST | Public | Anyone can register as `farmer` or `customer`. |
| `/api/v1/auth/login` | POST | Public | Standard credential check. |
| `/api/v1/auth/refresh` | POST | Public | Checks DB token validity to issue new access token. |
| `/api/v1/auth/logout` | POST | Customer, Farmer, Admin | Revokes the provided refresh token. |
| `/api/v1/auth/me` | GET | Customer, Farmer, Admin | Returns current user profile details. |
| `/api/v1/auth/farmer-only-test`| GET | Farmer, Admin | Verification endpoint restricted to farmers/admins. |
| `/api/v1/auth/admin-only-test` | GET | Admin | Verification endpoint restricted to admin accounts. |

## Risks / Trade-offs

- **[Risk] Refresh Token Database Bloat** -> *Mitigation*: Run a periodic cleanup task or cron job to delete expired or revoked tokens from the database.
- **[Risk] Revocation Latency** -> *Mitigation*: Validate token revocation on every refresh token exchange directly by checking database `is_revoked` fields.
