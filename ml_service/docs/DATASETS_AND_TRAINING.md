# Dataset and Training Guidelines

This document provides instructions on organizing agronomic datasets, running model training scripts, and deploying validated model assets for AgroGuide.

## 1. Directory Structure

Place datasets, training scripts, and output artifacts under the following folders:

```
ml_service/
├── datasets/          # Store raw/processed CSVs or crop imagery
│   ├── crop_recommendation.csv
│   ├── fertilizer_recommendation.csv
│   └── leaf_images/   # Subfolders with leaf classification sets
├── training/          # Training source scripts
│   ├── train_crop.py
│   └── train_fertilizer.py
└── models/            # Output model artifacts
    ├── crop_xgb.json
    └── fertilizer_dt.pkl
```

## 2. Dataset Specifications

### Crop Recommendation Dataset
- **Format**: CSV
- **Required Columns**:
  - `N`: Integer ratio of Nitrogen content in soil.
  - `P`: Integer ratio of Phosphorus content in soil.
  - `K`: Integer ratio of Potassium content in soil.
  - `temperature`: Celsius float values.
  - `humidity`: Relative percentage float values (10 to 100).
  - `ph`: Soil pH level float values (3.5 to 9.0).
  - `rainfall`: Float values in mm.
  - `label`: Target crop class labels.

### Plant Disease Dataset
- **Format**: Image folders structured by label names (e.g. `Potato___Early_blight`, `Tomato___Late_blight`).

---

## 3. Disabling Demo Mode for Production

To activate real model inference:
1. Ensure the generated model assets are placed in `ml_service/models/crop_xgb.json` and `ml_service/models/fertilizer_dt.pkl`.
2. Configure the environment variables in `docker-compose.yml` or your `.env` settings:
   ```env
   ML_DEMO_MODE=False
   CROP_MODEL_PATH=models/crop_xgb.json
   FERTILIZER_MODEL_PATH=models/fertilizer_dt.pkl
   ```

## 4. Minimum Quality Metrics

Do not set `ML_DEMO_MODE=False` in production unless your newly trained models satisfy the following evaluation metrics on validation tests:

| Model | Target Metric | Minimum Threshold |
|---|---|---|
| Crop Recommendation (XGBoost) | Accuracy | > 92% |
| Fertilizer Recommendation (DecisionTree) | F1-Score | > 88% |
| Plant Leaf Classifier (CNN / ResNet) | Validation Accuracy | > 90% |
