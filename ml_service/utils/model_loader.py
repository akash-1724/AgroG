import os
import pickle
import numpy as np
import xgboost as xgb

# Define constant crop and fertilizer names matching training schemas
CROP_CLASSES = ["rice", "papaya", "maize", "blackgram", "lentil", "banana"]
FERTILIZER_CLASSES = ["Urea", "DAP", "MOP", "NPK-19-19-19"]

class ModelLoader:
    def __init__(self):
        self.crop_model = None
        self.fertilizer_model = None
        self.load_models()

    def load_models(self):
        # Resolve path relative to this file
        current_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        
        crop_model_path = os.path.join(current_dir, "models", "crop_xgb.json")
        fertilizer_model_path = os.path.join(current_dir, "models", "fertilizer_dt.pkl")
        
        # Load XGBoost Crop Model
        if os.path.exists(crop_model_path):
            try:
                self.crop_model = xgb.XGBClassifier()
                self.crop_model.load_model(crop_model_path)
                print("Successfully loaded Crop Recommendation model.")
            except Exception as e:
                print(f"Error loading Crop Recommendation model: {e}")
        else:
            print(f"Warning: Crop model not found at {crop_model_path}")

        # Load Scikit-Learn Fertilizer Model
        if os.path.exists(fertilizer_model_path):
            try:
                with open(fertilizer_model_path, "rb") as f:
                    self.fertilizer_model = pickle.load(f)
                print("Successfully loaded Fertilizer Recommendation model.")
            except Exception as e:
                print(f"Error loading Fertilizer Recommendation model: {e}")
        else:
            print(f"Warning: Fertilizer model not found at {fertilizer_model_path}")

    def predict_crop(self, features: list[float]) -> list[dict]:
        """
        Takes soil metrics and returns crop recommendations with confidence.
        Input: [N, P, K, pH, temp, humidity, rainfall]
        """
        if self.crop_model is None:
            # Fallback mock predictions if model failed to load
            return [{"crop": "rice", "probability": 0.9}, {"crop": "maize", "probability": 0.1}]
            
        try:
            input_arr = np.array([features], dtype=np.float32)
            probs = self.crop_model.predict_proba(input_arr)[0]
            
            # Map predictions to class labels
            recommendations = []
            for idx, prob in enumerate(probs):
                if idx < len(CROP_CLASSES):
                    recommendations.append({
                        "crop": CROP_CLASSES[idx],
                        "probability": round(float(prob), 4)
                    })
            
            # Sort by probability descending
            recommendations.sort(key=lambda x: x["probability"], reverse=True)
            return recommendations
        except Exception as e:
            print(f"Inference error on crop recommendation: {e}")
            return [{"crop": "rice", "probability": 1.0}]

    def predict_fertilizer(self, features: list[float]) -> str:
        """
        Takes soil metrics and returns the recommended fertilizer type.
        Input: [N, P, K]
        """
        if self.fertilizer_model is None:
            return "NPK-19-19-19"
            
        try:
            input_arr = np.array([features], dtype=np.float32)
            class_idx = int(self.fertilizer_model.predict(input_arr)[0])
            if class_idx < len(FERTILIZER_CLASSES):
                return FERTILIZER_CLASSES[class_idx]
            return "NPK-19-19-19"
        except Exception as e:
            print(f"Inference error on fertilizer recommendation: {e}")
            return "NPK-19-19-19"

# Singleton instance
model_loader = ModelLoader()
