## 1. Environment and Configuration setup

- [x] 1.1 Verify/update environment variables in `ml_service` and docker compose for configurable model paths: `CROP_MODEL_PATH`, `FERTILIZER_MODEL_PATH`, and `ML_DEMO_MODE`.
- [x] 1.2 Update the `.env.example` file to document the new environment variables.

## 2. ML Service Schema Hardening & Health Endpoints

- [x] 2.1 Update Pydantic schemas in `ml_service` to validate input ranges: N-P-K (0-200), pH (3.5-9.0), temperature (0-50), humidity (10-100), rainfall (10-500).
- [x] 2.2 Expose a `/model-status` endpoint reporting load states (loaded, missing, demo-mode fallback) of all models.
- [x] 2.3 Refactor the `/health` endpoint to output a detailed dictionary containing service health, model statuses, and metadata.

## 3. Heuristic & Fallback Logic Hardening

- [x] 3.1 Refactor `ml_service` model loader to catch missing file exceptions gracefully, switching to demo/baseline mode and appending appropriate disclaimers and limitations to outputs.
- [x] 3.2 Add file size validation (max 5MB) and type validation in `/disease/detect` endpoint, returning safe disclaimers.

## 4. Dataset & Model Training Documentation

- [x] 4.1 Create `ml_service/docs/DATASETS_AND_TRAINING.md` outlining standard dataset structures, local directories, training scripts execution patterns, evaluation metric thresholds, and how to safely disable demo mode.

## 5. Frontend UI warning cards integration

- [x] 5.1 Update the soil crop predictor page (`frontend/src/app/recommendations/crop/page.tsx`) to render model state warning cards and disclaimers.
- [x] 5.2 Update the fertilizer suggestion page (`frontend/src/app/recommendations/fertilizer/page.tsx`) to display chemical safety disclaimer banners.
- [x] 5.3 Implement or update the leaf disease diagnosis form to include upload size boundaries (max 5MB), validation alerts, and diagnostic limit disclaimers.
