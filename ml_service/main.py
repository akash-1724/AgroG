import os
from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel, Field
import sentry_sdk
from ml_service.utils.model_loader import model_loader
from ml_service.utils.disease_classifier import classify_plant_disease

sentry_dsn = os.environ.get("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=1.0,
    )

app = FastAPI(title="AgroGuide ML Service", version="1.0.0")

# Request Schemas
class CropRecommendationInput(BaseModel):
    nitrogen: float = Field(..., description="Soil Nitrogen level (N)")
    phosphorus: float = Field(..., description="Soil Phosphorus level (P)")
    potassium: float = Field(..., description="Soil Potassium level (K)")
    ph: float = Field(..., description="Soil pH level")
    temperature: float = Field(..., description="Local Temperature in Celsius")
    humidity: float = Field(..., description="Local relative Humidity percentage")
    rainfall: float = Field(..., description="Average Rainfall in mm")

class FertilizerRecommendationInput(BaseModel):
    nitrogen: float = Field(..., description="Soil Nitrogen ratio (N)")
    phosphorus: float = Field(..., description="Soil Phosphorus ratio (P)")
    potassium: float = Field(..., description="Soil Potassium ratio (K)")

@app.get("/")
def read_root():
    return {
        "status": "ML Service online",
        "crop_model_loaded": model_loader.crop_model is not None,
        "fertilizer_model_loaded": model_loader.fertilizer_model is not None
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
    predictions = model_loader.predict_crop(features)
    return {"recommendations": predictions}

@app.post("/recommendations/fertilizer")
async def recommend_fertilizer(payload: FertilizerRecommendationInput):
    """Recommends fertilizer based on N-P-K mineral levels of the soil."""
    features = [
        payload.nitrogen,
        payload.phosphorus,
        payload.potassium
    ]
    fertilizer = model_loader.predict_fertilizer(features)
    return {
        "recommended_fertilizer": fertilizer,
        "guideline": f"Based on your N={payload.nitrogen}, P={payload.phosphorus}, K={payload.potassium} ratios, apply {fertilizer} as recommended."
    }

@app.post("/disease/detect")
async def detect_disease(file: UploadFile = File(...)):
    """Receives leaf image files and returns predicted disease, confidence level, and remedy."""
    # Validate file format
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid image type. Only JPEG and PNG are supported."
        )
        
    try:
        content = await file.read()
        prediction = classify_plant_disease(content)
        return prediction
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running plant disease detection: {str(e)}"
        )

