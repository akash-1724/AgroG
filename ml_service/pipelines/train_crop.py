import os
import numpy as np
import xgboost as xgb

def train_and_serialize_crop_model():
    print("Training mock Crop Recommendation XGBoost model...")
    # Features: [Nitrogen, Phosphorus, Potassium, pH, Temperature, Humidity, Rainfall]
    X = np.array([
        [90, 42, 43, 6.5, 20.8, 82.0, 202.9], # rice
        [85, 58, 41, 7.0, 21.7, 80.3, 226.6], # rice
        [60, 55, 44, 5.7, 23.0, 82.3, 263.9], # papaya
        [80, 35, 40, 6.2, 25.0, 80.0, 150.0], # maize
        [40, 72, 20, 5.5, 24.4, 73.0, 60.8],  # blackgram
        [20, 60, 15, 6.8, 26.0, 85.0, 100.0], # lentil
        [100, 30, 50, 6.5, 28.0, 70.0, 180.0] # banana
    ])
    
    # Target classes: 0: rice, 1: papaya, 2: maize, 3: blackgram, 4: lentil, 5: banana
    y = np.array([0, 0, 1, 2, 3, 4, 5])
    
    # Train XGBoost Classifier
    model = xgb.XGBClassifier(
        n_estimators=10,
        max_depth=3,
        learning_rate=0.1,
        objective="multi:softprob",
        num_class=6
    )
    model.fit(X, y)
    
    # Ensure models directory exists
    os.makedirs("models", exist_ok=True)
    
    # Serialize model to JSON
    model_path = "models/crop_xgb.json"
    model.save_model(model_path)
    print(f"Crop model serialized successfully to {model_path}")

if __name__ == "__main__":
    train_and_serialize_crop_model()
