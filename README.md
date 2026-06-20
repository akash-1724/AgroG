# AgroGuide Monorepo Baseline

AgroGuide is a production-quality AI-powered AgriTech platform designed to assist farmers and agricultural users with crop selection, fertilizer recommendations, and plant leaf disease diagnostic analytics.

---

## Repository Structure

The monorepo contains the following workspace services:
- `/backend`: FastAPI backend exposing authentication, marketplace transactions, geolocation farmers search, and streaming LLM chat gateways.
- `/frontend`: Next.js App Router client with earth-toned tailwind layouts, state context, and react hook form integration.
- `/ml_service`: FastAPI machine learning microservice containing Scikit-Learn/XGBoost models for crop recommendation, fertilizer calculation, and PIL leaf classification.
- `/openspec`: Capability requirements, technical design records, and active feature change task sheets.

---

## Local Development Configuration

Before starting, copy the configuration template to initialize your local environment variables:
```bash
cp .env.example .env
```

Review `.env` and fill in required API keys and service credentials for your environment.

---

## Running Locally

### 1. Backend Service
Make sure you have a running PostgreSQL instance and Redis server configured in `.env`, then:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

To load sample marketplace listings, farmers, educational articles, and verified external image URLs after migrations:
```bash
cd backend
PYTHONPATH=. ../venv/bin/python -m app.seed_sample_data
```

Seeded demo users use this password: `AgroGuideDemo123!`

### 2. ML Service
```bash
cd ml_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 3. Frontend App
```bash
cd frontend
npm install
npm run dev
```

---

## Docker Compose Orchestration

To compile and launch the entire ecosystem (database, cache, backend, ML service, and client) inside containerized services:

```bash
# Start all containers in the background
docker compose up -d --build

# View runtime container logs
docker compose logs -f
```

---

## Verification & Health Check Endpoints

Once services are running, you can verify their status:

- **Backend Health Check**:
  ```bash
  curl http://localhost:8000/health
  # Response: {"status": "healthy", "service": "AgroGuide"}
  ```

- **ML Service Health Check**:
  ```bash
  curl http://localhost:8001/health
  # Response: {"status": "healthy", "crop_model_loaded": true, "fertilizer_model_loaded": true}
  ```

- **Frontend App**: Open [http://localhost:3000](http://localhost:3000) in your web browser.
 
---

## Running Automated Tests (Pytest Suites)

AgroGuide comes with comprehensive automated test suites using `pytest`.

### 1. Run Backend Tests
To test user authentication, RBAC authorizations, listings, orders, nearby farmer discoveries, and assistant fallbacks:
```bash
cd backend
PYTHONPATH=. ../venv/bin/pytest app/tests/test_backend.py
```

### 2. Run ML Service Tests
To test crop/fertilizer inputs validations, model status loaded states, 5MB limits, and classifier fallbacks:
```bash
cd ml_service
PYTHONPATH=. ../venv/bin/pytest tests/test_ml.py
```

---

## Integration & Verification Scripts (Docker/Local)

You can run automated integration testing scripts to verify database relationships, authentication state-machines, and Role-Based Access Control logic:

### 1. Verify Authentication & RBAC
```bash
docker compose exec backend python verify_auth.py
# Or locally inside /backend: python verify_auth.py
```

### 2. Verify Marketplace Listings & Orders
```bash
docker compose exec backend python verify_marketplace.py
# Or locally inside /backend: python verify_marketplace.py
```

---

## Known Heuristic Fallbacks (Non-Production)

- **Plant Leaf Disease Classification**: The `/disease/detect` classifier currently runs a deterministic color-channel pixel statistical model mapped to mock labels inside `ml_service/utils/disease_classifier.py` for sandbox/developer baseline tests. This is a baseline placeholder and is not production-grade machine learning.
