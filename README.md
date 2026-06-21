# AgroGuide

AgroGuide is a collaborative AgriTech learning project designed to assist farmers and customers. It features a localized product marketplace, crop and fertilizer recommendation tools, and an AI-powered chat assistant.

---

## Key Capabilities

* **Authentication & Role-Based Access Control (RBAC)**: Secure registration and login workflows for different roles (Farmer, Customer, and Admin) using JWT access tokens, revocable refresh tokens, and Google OAuth 2.0.
* **Farmer Marketplace & Listings**: Farmers can create and manage their listings with product details, stock quantities, and pricing. Customers can search and browse products.
* **Cart & Checkout**: A complete shopping cart and order creation checkout flow.
* **Farmer Public Profiles**: Dedicated pages presenting farmer listings, farm descriptions, and contact info.
* **Reviews and Ratings**: Customer feedback loop with crop star ratings and comments.
* **Crop & Fertilizer Recommendations**: Machine learning models hosted in an isolated service to suggest optimal crops (using XGBoost) and fertilizer blends (using a Decision Tree) based on soil mineral ratios (N-P-K) and environmental conditions.
* **Weather-Aware Recommendations**: Integrates with the Open-Meteo API to fetch real-time climate inputs (temperature, humidity, precipitation) based on location coordinates, with input-bounds clipping for model safety.
* **Market Price Trends**: Visualizes historical and mock price trend data for agricultural commodities.
* **Educational Resources**: A catalog of farmer-focused resources and tutorials filtered by agricultural topics.
* **AI Agriculture Assistant**: A conversational assistant powered by Google's Gemini API (`gemini-1.5-flash`), with a rule-based fallback mode for baseline demonstration.
* **Nearby Farmer Discovery**: Location-aware discovery of farmers and public listings near the user's coordinates.
* **Admin Analytics**: Dashboards providing system administrators with operational metrics on platform activity.

---

## Project Origin

AgroGuide was started as a free-time collaborative project by Akash and Christina. The initial idea was selected by Christina from the senior-project topic collection published at [SJCET Project Showcase](https://project.sjcet.in/).

The project is built with AI-assisted development tools, but development is guided through a spec-driven workflow using OpenSpec. Features are planned, specified, implemented, verified, and reviewed in phases rather than being generated as unstructured code.

---

## Technology Stack

* **Frontend**: Next.js (App Router), React, Tailwind CSS, TypeScript
* **Backend**: FastAPI, SQLAlchemy 2.0 (Async), Uvicorn, PostgreSQL, Redis (Caching)
* **ML Service**: FastAPI, Uvicorn, Scikit-Learn, XGBoost, NumPy, Pillow (PIL)
* **API Clients & Services**: httpx, Open-Meteo API, Cloudinary (Media hosting)

---

## Repository Structure

```
├── backend/            # FastAPI REST API, db models, Alembic migrations, test suites
├── frontend/           # Next.js web application pages and React UI components
├── ml_service/         # Python ML service, trained model binaries, inference utilities
├── openspec/           # Specifications, system requirements, and tasks archive
├── docker-compose.yml  # Multi-container orchestration config
└── README.md           # Repository documentation
```

---

## Current Implementation Status

| Area | Status | Notes |
| :--- | :--- | :--- |
| **Authentication & RBAC** | Implemented | Supports local credentials and Google OAuth 2.0. |
| **Marketplace & Listings** | Implemented | Product listings, inventory tracking, and search functionality. |
| **Cart & Order Flow** | Implemented | Cart persistence and order creation checkout steps. |
| **Farmer Profiles & Reviews** | Implemented | Public farmer profiles, star ratings, and text reviews. |
| **Crop & Fertilizer Advisor** | Implemented | XGBoost and Decision Tree models served via the ML service. |
| **Weather-Aware Recommendations** | Implemented | Integrates Open-Meteo current weather with automatic input-bounds clipping. |
| **Leaf Disease Diagnosis** | Demo/Baseline | Employs a simple color-heuristic algorithm as a placeholder. No neural network is used. |
| **Crop Price Trends** | Demo/Baseline | Renders mock crop price charts and trends. |
| **AI Agriculture Assistant** | Optional Configuration | Uses Gemini API. Falls back to a rule-based mock advisor if `GEMINI_API_KEY` is missing. |
| **Image Uploads** | Optional Configuration | Fully supports Cloudinary media uploads if `CLOUDINARY_URL` is configured. |

---

## Environment Variables

To set up environment variables for the system:

1. Copy the configuration template to initialize your local `.env` file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in the required values. Never commit your `.env` file to version control.
3. Private keys (such as `JWT_SECRET`, `JWT_REFRESH_SECRET`, `GOOGLE_CLIENT_SECRET`, `CLOUDINARY_URL`, and `GEMINI_API_KEY`) must remain secure and blank in template files.
4. Integrations like Google OAuth, Cloudinary, and Gemini are optional; the application will fall back to simulation/demo behaviors if their respective keys are not provided.

---

## Local Setup

### 1. Backend Service
Make sure you have a running PostgreSQL instance and Redis server configured in `.env`, then:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
To run the sample data seed script (after applying database migrations):
```bash
PYTHONPATH=. python app/seed_sample_data.py
```
*(Seeded demo users are created with the password: `AgroGuideDemo123!`)*

### 2. ML Service
```bash
cd ml_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 3. Frontend Application
```bash
cd frontend
npm install
npm run dev
```

---

## Docker Setup

To compile and launch the entire stack (PostgreSQL database, Redis cache, Backend API, ML service, and Frontend app) using Docker Compose:

```bash
# Start all containerized services in the background
docker compose up -d --build

# Inspect runtime logs
docker compose logs -f
```

---

## Testing and Verification

### 1. Run Automated Test Suites
With your virtual environments active, you can execute the test suites from the respective service directories:

* **Backend Tests**:
  ```bash
  cd backend
  PYTHONPATH=. pytest app/tests/test_backend.py
  ```

* **ML Service Tests**:
  ```bash
  cd ml_service
  PYTHONPATH=. pytest tests/test_ml.py
  ```

* **Frontend Verification**:
  ```bash
  cd frontend
  npm run lint
  npx tsc --noEmit
  npm run build
  ```

### 2. Integration & Verification Scripts
Run automated integration logic tests to verify relationships and RBAC rules:
```bash
# If running via Docker Compose
docker compose exec backend python verify_auth.py
docker compose exec backend python verify_marketplace.py

# If running locally (from within the /backend directory)
python verify_auth.py
python verify_marketplace.py
```

---

## Known Limitations

* **Plant Disease Scanner**: Leaf disease classification uses a deterministic color-channel pixel statistical heuristic helper. It is not an actual neural network and should be treated purely as a baseline demo/simulation.
* **Crop/Fertilizer ML Output**: Model prediction accuracy depends on the generalization bounds of the sample training datasets used for model artifacts.
* **Weather & Market Price Data**: Renders static/fallback mock records if Open-Meteo or other data providers are unreachable.
* **Advisory Disclaimer**: This project is built for educational/personal-learning purposes. Predictions and suggestions must not be used as professional agricultural advice.

---

## Contributors

* **Akash** — Project contributor and maintainer. [akash-1724](https://github.com/akash-1724)
* **Christina** — Project contributor.

> Christina's profile link can be added later when available.

---

## License

This project is licensed under the terms of the MIT License. See the [LICENSE](LICENSE) file for details.
