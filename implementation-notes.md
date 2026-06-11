# AgroGuide Implementation Notes - Core Data, Auth, and RBAC

This document captures architecture decisions, tradeoffs, implementation changes, and Git commits for the auth and database stabilization.

## Git Commits Log

| Timestamp | Commit SHA | Description |
| :--- | :--- | :--- |
| 2026-06-10T20:38:00+05:30 | 1f524b7 | Create RefreshToken model and link user relationships |
| 2026-06-10T20:41:00+05:30 | 29ab15d | Make FarmerProfile fields nullable for empty profile creation on registration |
| 2026-06-10T20:48:00+05:30 | c19b177 | Generate and run Alembic database migrations to create core tables and refresh tokens |
| 2026-06-10T20:53:00+05:30 | 08015b4 | Update /register endpoint to block admin signup and auto-initialize empty FarmerProfile |
| 2026-06-10T20:58:00+05:30 | 2af2ec9 | Persist refresh tokens in database on successful login (/token and /token-json) |
| 2026-06-10T21:05:00+05:30 | 761d511 | Implement /refresh endpoint validating tokens in database |
| 2026-06-10T21:12:00+05:30 | eedc914 | Implement /logout endpoint revoking tokens in database and clearing cookies |
| 2026-06-10T21:17:00+05:30 | 74c080a | Implement /me endpoint to fetch current authenticated user profile |
| 2026-06-10T21:22:00+05:30 | 0a42bc8 | Implement get_current_user_optional dependency in deps.py to prevent import failures |
| 2026-06-10T21:28:00+05:30 | b66e520 | Implement role-protected verification routes (/farmer-only-test and /admin-only-test) |
| 2026-06-10T21:35:00+05:30 | fedd6b9 | Create automated verification test script for auth and RBAC flow |
| 2026-06-10T22:54:00+05:30 | 59d2c97 | Fix backend requirements, bypass passlib bcrypt wraps via direct bcrypt, update tasks |
