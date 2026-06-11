## Why

AgroGuide needs a secure, robust, and clean database, authentication, and role-based access control (RBAC) foundation before launching marketplace or dashboard transactions. While Google OAuth is deferred, we must establish a production-style email/password register/login flow, short-lived JWT access tokens, and a revocable database-persisted refresh token flow with explicit logout triggers.

## What Changes

This change implements and consolidates the core database auth layers:
- **Authentication**: Email/password registration and login with bcrypt hashing.
- **Refresh Token Lifecycle**: Database-persisted, unique refresh tokens with revocation on logout and new access token generation on refresh request.
- **Enforced Authorization**: FastAPI router role guards for `farmer`, `customer`, and `admin` roles, restricting registration and data access.
- **Security Control**: Restricting public admin registration options and ensuring farmer registration automatically creates a corresponding farmer profile.

## Capabilities

### New Capabilities
<!-- None. Consolidating the core database auth schemas under existing specifications. -->

### Modified Capabilities
- `auth-and-rbac`: Aligning spec requirements to enforce simple email/password register/login, refresh token database revocation, logout endpoint behavior, and RBAC endpoint validations.
