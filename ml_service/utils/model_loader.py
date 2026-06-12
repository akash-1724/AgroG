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
        
        # Load configs from environment
        self.crop_path = os.environ.get("CROP_MODEL_PATH", "models/crop_xgb.json")
        self.fertilizer_path = os.environ.get("FERTILIZER_MODEL_PATH", "models/fertilizer_dt.pkl")
        self.demo_mode = os.environ.get("ML_DEMO_MODE", "True").lower() in ["true", "1", "yes"]

        # Track loading status
        self.crop_status = "demo"
        self.fertilizer_status = "demo"
        self.disease_status = "demo" # Always demo/heuristic baseline in this phase

        self.load_models()

    def load_models(self):
        if self.demo_mode:
            print("ML_DEMO_MODE is active. Bypassing model loading, operating in demo mode.")
            return

        current_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        
        # Resolve absolute paths if not absolute
        c_path = self.crop_path if os.path.isabs(self.crop_path) else os.path.join(current_dir, self.crop_path)
        f_path = self.fertilizer_path if os.path.isabs(self.fertilizer_path) else os.path.join(current_dir, self.fertilizer_path)
        
        # Load XGBoost Crop Model
        if os.path.exists(c_path):
            try:
                self.crop_model = xgb.XGBClassifier()
                self.crop_model.load_model(c_path)
                self.crop_status = "loaded"
                print(f"Successfully loaded Crop Recommendation model from {c_path}.")
            except Exception as e:
                print(f"Error loading Crop Recommendation model: {e}")
                self.crop_status = "demo"
        else:
            print(f"Warning: Crop model not found at {c_path}. Falling back to demo mode.")
            self.crop_status = "demo"

        # Load Scikit-Learn Fertilizer Model
        if os.path.exists(f_path):
            try:
                with open(f_path, "rb") as f:
                    self.fertilizer_model = pickle.load(f)
                self.fertilizer_status = "loaded"
                print(f"Successfully loaded Fertilizer Recommendation model from {f_path}.")
            except Exception as e:
                print(f"Error loading Fertilizer Recommendation model: {e}")
                self.fertilizer_status = "demo"
        else:
            print(f"Warning: Fertilizer model not found at {f_path}. Falling back to demo mode.")
            self.fertilizer_status = "demo"

    def predict_crop(self, features: list[float]) -> tuple[list[dict], str]:
        """
        Takes soil metrics and returns crop recommendations with confidence and status.
        Input: [N, P, K, pH, temp, humidity, rainfall]
        """
        disclaimer = "Advisory only. Always verify with local agricultural extension services."
        
        if self.crop_model is None or self.crop_status == "demo":
            # Fallback mock predictions if model failed or demo mode is active
            mock_preds = [{"crop": "rice", "probability": 0.9}, {"crop": "maize", "probability": 0.1}]
            return mock_preds, "demo"
            
        try:
            input_arr = np.array([features], dtype=np.float32)
            probs = self.crop_model.predict_proba(input_arr)[0]
            
            recommendations = []
            for idx, prob in enumerate(probs):
                if idx < len(CROP_CLASSES):
                    recommendations.append({
                        "crop": CROP_CLASSES[idx],
                        "probability": round(float(prob), 4)
                    })
            
            recommendations.sort(key=lambda x: x["probability"], reverse=True)
            return recommendations, "real"
        except Exception as e:
            print(f"Inference error on crop recommendation: {e}")
            return [{"crop": "rice", "probability": 1.0}], "demo"

    def predict_fertilizer(self, features: list[float]) -> tuple[str, str]:
        """
        Takes soil metrics and returns recommended fertilizer type and status.
        Input: [N, P, K]
        """
        if self.fertilizer_model is None or self.fertilizer_status == "demo":
            # Heuristic rule-based fallback if no model exists or in demo mode
            # Standard ratio check: if N low, suggest Urea. If P low, suggest DAP. If K low, suggest MOP.
            n, p, k = features
            if n < 30:
                rec = "Urea"
            elif p < 30:
                rec = "DAP"
            elif k < 30:
                rec = "MOP"
            else:
                rec = "NPK-19-19-19"
            return rec, "demo"
            
        try:
            input_arr = np.array([features], dtype=np.float32)
            class_idx = int(self.fertilizer_model.predict(input_arr)[0])
            if class_idx < len(FERTILIZER_CLASSES):
                return FERTILIZER_CLASSES[class_idx], "real"
            return "NPK-19-19-19", "real"
        except Exception as e:
            print(f"Inference error on fertilizer recommendation: {e}")
            return "NPK-19-19-19", "demo"

# Singleton instance
model_loader = ModelLoader()
