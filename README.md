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

Review `.env` and fill in API keys or Sentry details if using them in production.

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

## Known Heuristic Fallbacks (Non-Production)

- **Plant Leaf Disease Classification**: The `/disease/detect` classifier currently runs a deterministic color-channel pixel statistical model mapped to mock labels inside `ml_service/utils/disease_classifier.py` for sandbox/developer baseline tests. This is a baseline placeholder and is not production-grade machine learning.
