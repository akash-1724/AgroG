# AgroGuide Production Readiness & Security Checklist

This document details critical pre-flight checks, security measures, and rollback protocols before launching AgroGuide in a production environment.

## 1. Secrets & Environment Variables Checklist

Ensure **all** production environments use real, secure, and uniquely generated values. **Never commit secrets to VCS.**

### Backend Secrets
| Variable Name | Description | Production Requirement |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | Must use SSL (`sslmode=require`). Do not use pooler mode during Alembic migrations. |
| `REDIS_URL` | Redis connection string | Must use secure protocol (`rediss://`). |
| `JWT_SECRET` | JWT access-token signing secret | Must be a secure 32+ character hex string (e.g., `openssl rand -hex 32`). |
| `JWT_REFRESH_SECRET` | JWT refresh-token signing secret | Must be different from `JWT_SECRET` and generated securely. |

### ML Service Secrets
| Variable Name | Description | Production Requirement |
|---|---|---|
| `CROP_MODEL_PATH` | Path to crop model file | Path to verified `.joblib` / `.bin` classifier artifact. |
| `FERTILIZER_MODEL_PATH` | Path to fertilizer model file | Path to verified `.joblib` / `.bin` classifier artifact. |
| `ML_DEMO_MODE` | Boolean flag | Set to `False` once trained ML model artifacts are loaded. |
| `MAX_IMAGE_UPLOAD_MB` | Image file upload limit | Set to `5` to prevent denial-of-service via large image payloads. |

---

## 2. Pre-Flight Security Checklist

- [ ] **SSL/TLS Certificates**: Enforce HTTPS on all domain endpoints (Next.js, FastAPI Backend, and ML Service).
- [ ] **Database Encryption**: Verify PostgreSQL database connections require TLS/SSL.
- [ ] **Cors Settings**: Restrict FastAPI backend `ALLOW_ORIGINS` strictly to the production frontend domain (avoid `*`).
- [ ] **Password Hashing**: Ensure bcrypt rounds are sufficient and secure.
- [ ] **Model Isolation**: Double-check that inputs to the ML service models are validated strictly on bounds (N-P-K, pH, temperature, humidity, rainfall) to prevent payload exploits.

---

## 3. Rollback & Recovery Strategy

In the event of a critical failure after deployment:

### Application Rollback
- **Frontend (Vercel)**:
  1. Navigate to the **Deployments** tab in Vercel.
  2. Select the previous stable deployment.
  3. Click **Instant Rollback**.
- **Backend / ML Service (Render)**:
  1. Go to the service page and select the **Deployments** history.
  2. Click **Rollback** on the last known working git commit build.

### Database Rollback
- In case of a bad Alembic migration, roll back the schema schema one level:
  ```bash
  DATABASE_URL="prod-uri" alembic downgrade -1
  ```
- Make regular, automated backups of the PostgreSQL DB using your host's integrated backup tool (e.g., Supabase daily backups).

---

## 4. Known System Limitations

1. **ML Advisory Fallbacks**:
   - The ML service uses a rule-based/mock fallback model when ML model files are missing or loading fails.
   - Predictions are *approximate* and for educational/demonstrative use only.
2. **SQLite vs PostgreSQL**:
   - Local development uses SQLite in-memory/disk databases, while production uses PostgreSQL.
   - Spatial math (Haversine queries) has custom mock bindings configured for SQLite tests. Ensure full SQL compliance is manually reviewed.
