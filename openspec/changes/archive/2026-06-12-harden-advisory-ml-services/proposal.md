## Why

The current implementation of the ML service has basic endpoints for crop recommendations, fertilizer suggestions, and plant disease diagnosis, but they lack clean service boundaries, configurable environment paths, input validation ranges, model artifact load checks, and safety guidelines. Hardening the ML service ensures the system is resilient to missing model files, operates safely in baseline demo-mode without claiming agronomic certainty, and provides descriptive diagnostic warnings and disclaimers to farmers.

## What Changes

This change hardens the ML inference boundaries, schemas, and endpoints:
- Adds range validation rules for soil inputs (nitrogen, phosphorus, potassium, ph, temperature, humidity, rainfall) inside request schemas.
- Adds file type and size verification checks for plant disease image uploads.
- Implements dynamic model state detection exposing loaded/missing status, and switches cleanly to safe rule-based baseline/demo-mode.
- Enhances response schemas to return model status, confidence metrics, and clear agronomic disclaimers warning against dangerous chemical dosages.
- Exposes ML service `/health` and `/model-status` endpoints.
- Modifies frontend pages `/recommendations/crop`, `/recommendations/fertilizer`, and `/disease-detection` (if renamed or needed) to render warning banners for baseline/demo mode and display diagnostic results safely.

## Capabilities

### New Capabilities
<!-- None. We are hardening existing capabilities. -->

### Modified Capabilities
- `crop-recommendation`: Enforces input range constraints, configures environment-driven model loading, and exposes model fallback state.
- `fertilizer-recommendation`: Adds validation limits, rule-based fallbacks, and disclaimers.
- `plant-disease-detection`: Validates image uploads, catches missing model exceptions safely, and enforces safety disclaimer indicators.

## Impact

- **ML Service**: Adds robust schema validation, model loader status reporting, fallback simulation configs, and healthy/ready checks.
- **Backend Service**: Validates payload schemas and handles upstream ML connection failures cleanly.
- **Frontend App**: Updates pages to clearly present model status flags, disclaimer text, and handle validation errors gracefully.
