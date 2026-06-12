## Context

AgroGuide separates application logic (FastAPI + Postgres) from machine learning logic (an isolated FastAPI `ml_service` wrapper). Currently, the ML service implements baseline heuristic mappings for crop recommendation, fertilizer selection, and plant disease diagnosis. However, it lacks environment configuration controls, input range validators, model file load state checking, health checks, and user-facing warning disclaimers. This design introduces robust service boundaries, configurable env-based loader properties, and clear disclaimer policies.

## Goals / Non-Goals

**Goals:**
- Separate validation schemas, inference pipelines, and model loaders inside `ml_service`.
- Make model paths and fallback configurations dynamically configurable through environment variables.
- Add `/health` and `/model-status` endpoints for service orchestration checkups.
- Enforce strict input range constraints (Pydantic / Zod) for crop (N, P, K, pH, temp, humidity, rain) and fertilizer (N, P, K) inputs.
- Enforce image upload boundaries (max 5MB size limit, content-type filters) for disease classification.
- Modify the JSON payload outputs to include: `model_status`, `confidence`, and descriptive advisory disclaimers.
- Update frontend screens (Soil Crop Predictor, Fertilizer prescription, Leaf Disease Scanner) to parse the model status and display a visible disclaimer or warning banner.
- Document dataset specifications, model artifact locations, training setup guidelines, and validation metrics needed to transition from demo-mode to real models.

**Non-Goals:**
- Training or downloading massive model weights in this phase.
- Modifying crop listing or ordering flow logic.
- Implementing databases or persistence layers inside the ML service (all history is saved on the backend layer).

## Decisions

### 1. Model State Configuration
We will introduce the following environment configuration options in the ML service:
* `CROP_MODEL_PATH`: Location of the XGBoost json model file (defaults to `models/crop_xgb.json`).
* `FERTILIZER_MODEL_PATH`: Location of the DecisionTree pkl model file (defaults to `models/fertilizer_dt.pkl`).
* `ML_DEMO_MODE`: Boolean flag forcing fallback mode even if model files exist (defaults to `True` for baseline demonstration).
* `MAX_IMAGE_UPLOAD_MB`: Integer setting max image size in megabytes (defaults to `5`).

*Alternatives Considered*: Crash service on startup if model files are missing. However, utilizing fallback mode allows the platform to run seamlessly without model dependencies during dev/local testing.

### 2. Output Schema Standardisation
All three advisory routes will output a standardized payload schema:
```json
{
  "prediction": "string or ranked list",
  "confidence": 0.85,
  "model_status": "demo | real",
  "disclaimer": "Advisory only. Consult certified agronomists before chemical application.",
  "limitations": "Predictions simulated on regional baseline approximations."
}
```

### 3. Dataset & Training Documentation
A document at `ml_service/docs/DATASETS_AND_TRAINING.md` will define:
- Standard dataset folder layouts: `ml_service/datasets/`.
- Training execution logic location: `ml_service/training/`.
- Switchover parameters: How to toggle `ML_DEMO_MODE` env to `False`.
- Minimum qualification metrics: (e.g. F1-score > 0.85, Accuracy > 0.90) required before deployment.

## Risks / Trade-offs

- **Risk** -> Users could apply dangerous chemical dosages based on mock fertilizer rules.
  - **Mitigation** -> Expose highly visible warning cards and disclaimer banners on both frontend forms and backend REST payloads, advising consultation with local authorities before ordering materials.
