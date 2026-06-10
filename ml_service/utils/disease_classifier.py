import io
import numpy as np
from PIL import Image

DISEASES = [
    {"label": "Tomato Late Blight", "remedy": "Apply copper-based fungicides and destroy affected plants."},
    {"label": "Potato Early Blight", "remedy": "Apply chlorothalonil or copper fungicides, and ensure crop rotation."},
    {"label": "Apple Scab", "remedy": "Apply captan or sulphur-based fungicides, and clear leaf litter under trees."},
    {"label": "Healthy Leaf", "remedy": "No disease detected. Continue normal crop care and watering schedules."}
]

def classify_plant_disease(image_bytes: bytes) -> dict:
    """
    Placeholder image classification pipeline.
    Loads leaf image bytes, resizes to standard input dimensions (224x224),
    extracts color features (mean RGB) to dynamically simulate ML classification.
    """
    try:
        # Load and verify image
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB")
        image_resized = image.resize((224, 224))
        
        # Extract basic color features to add deterministic variation based on the image
        img_array = np.array(image_resized)
        mean_r = float(np.mean(img_array[:, :, 0]))
        mean_g = float(np.mean(img_array[:, :, 1]))
        mean_b = float(np.mean(img_array[:, :, 2]))
        
        # Simple heuristic mapping mean color channel to classes
        score = (mean_r + mean_g - mean_b) % len(DISEASES)
        result_idx = int(score)
        
        selected = DISEASES[result_idx]
        confidence = 0.85 + (mean_g / 1000.0) # mock confidence score
        confidence = min(0.99, max(0.60, float(confidence)))
        
        return {
            "predicted_disease": selected["label"],
            "confidence": round(confidence, 4),
            "remedy": selected["remedy"]
        }
    except Exception as e:
        print(f"Image processing error: {e}")
        # Default fallback
        return {
            "predicted_disease": "Healthy Leaf",
            "confidence": 1.0000,
            "remedy": "No disease detected. Continue normal crop care."
        }
