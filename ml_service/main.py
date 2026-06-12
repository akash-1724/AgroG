import os
from fastapi import FastAPI, HTTPException, File, UploadFile, status
from pydantic import BaseModel, Field
from ml_service.utils.model_loader import model_loader
from ml_service.utils.disease_classifier import classify_plant_disease

app = FastAPI(title="AgroGuide ML Service", version="1.0.0")

# Request Schemas with explicit bounds validation
class CropRecommendationInput(BaseModel):
    nitrogen: float = Field(..., ge=0.0, le=200.0, description="Soil Nitrogen level (N) in ppm")
    phosphorus: float = Field(..., ge=0.0, le=200.0, description="Soil Phosphorus level (P) in ppm")
    potassium: float = Field(..., ge=0.0, le=200.0, description="Soil Potassium level (K) in ppm")
    ph: float = Field(..., ge=3.5, le=9.0, description="Soil pH level")
    temperature: float = Field(..., ge=0.0, le=50.0, description="Local Temperature in Celsius")
    humidity: float = Field(..., ge=10.0, le=100.0, description="Local relative Humidity percentage")
    rainfall: float = Field(..., ge=10.0, le=500.0, description="Average Rainfall in mm")

class FertilizerRecommendationInput(BaseModel):
    nitrogen: float = Field(..., ge=0.0, le=200.0, description="Soil Nitrogen ratio (N)")
    phosphorus: float = Field(..., ge=0.0, le=200.0, description="Soil Phosphorus ratio (P)")
    potassium: float = Field(..., ge=0.0, le=200.0, description="Soil Potassium ratio (K)")
    crop_type: str = Field(default="rice", description="Target Crop Type")

@app.get("/")
def read_root():
    return {
        "status": "ML Service online",
        "demo_mode_active": model_loader.demo_mode,
        "crop_model_status": model_loader.crop_status,
        "fertilizer_model_status": model_loader.fertilizer_status,
        "disease_model_status": model_loader.disease_status
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "demo_mode": model_loader.demo_mode,
        "crop_model": model_loader.crop_status,
        "fertilizer_model": model_loader.fertilizer_status,
        "disease_model": model_loader.disease_status
    }

@app.get("/model-status")
def get_model_status():
    """Reports the explicit state of ML model artifacts and fallbacks."""
    return {
        "demo_mode": model_loader.demo_mode,
        "models": {
            "crop_recommendation": {
                "status": model_loader.crop_status,
                "configured_path": model_loader.crop_path,
                "type": "XGBoost Classifier"
            },
            "fertilizer_recommendation": {
                "status": model_loader.fertilizer_status,
                "configured_path": model_loader.fertilizer_path,
                "type": "Decision Tree Classifier"
            },
            "disease_detection": {
                "status": model_loader.disease_status,
                "type": "Color Heuristic Baseline Classifier"
            }
        }
    }

@app.post("/recommendations/crop")
async def recommend_crop(payload: CropRecommendationInput):
    """Predicts suitable crops based on soil nutrients and climatic parameters."""
    features = [
        payload.nitrogen,
        payload.phosphorus,
        payload.potassium,
        payload.ph,
        payload.temperature,
        payload.humidity,
        payload.rainfall
    ]
    predictions, status_code = model_loader.predict_crop(features)
    
    return {
        "recommendations": predictions,
        "model_status": status_code,
        "disclaimer": "Advisory only. Always consult with local certified agricultural extension workers before seeding.",
        "limitations": "ML predictions are statistical approximations trained on general climate zones."
    }

@app.post("/recommendations/fertilizer")
async def recommend_fertilizer(payload: FertilizerRecommendationInput):
    """Recommends fertilizer based on N-P-K mineral levels of the soil."""
    features = [
        payload.nitrogen,
        payload.phosphorus,
        payload.potassium
    ]
    fertilizer, status_code = model_loader.predict_fertilizer(features)
    
    return {
        "recommended_fertilizer": fertilizer,
        "model_status": status_code,
        "guideline": f"Based on your N={payload.nitrogen}, P={payload.phosphorus}, K={payload.potassium} ratios, apply {fertilizer} as recommended.",
        "disclaimer": "Advisory warning: Applying high concentration chemicals without soil test confirmation may degrade soil quality.",
        "limitations": "Formulations are generated using a heuristic diagnostic baseline."
    }

@app.post("/disease/detect")
async def detect_disease(file: UploadFile = File(...)):
    """
    Receives leaf image files and returns predicted disease, confidence level, and remedy.
    Enforces format and size limits.
    """
    # Validate file format
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image type. Only JPEG, JPG and PNG are supported."
        )

    # Validate file size (max upload size from environment in MB, default to 5MB)
    max_mb = int(os.environ.get("MAX_IMAGE_UPLOAD_MB", "5"))
    max_bytes = max_mb * 1024 * 1024

    try:
        content = await file.read()
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Image file size exceeds limit of {max_mb}MB."
            )
            
        prediction = classify_plant_disease(content)
        return prediction
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running plant disease detection: {str(e)}"
        )
