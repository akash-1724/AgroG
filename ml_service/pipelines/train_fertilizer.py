import os
import pickle
import numpy as np
from sklearn.tree import DecisionTreeClassifier

def train_and_serialize_fertilizer_model():
    print("Training mock Fertilizer Recommendation DecisionTree model...")
    # Features: [Nitrogen, Phosphorus, Potassium]
    X = np.array([
        [100, 0, 0],   # Urea (High N)
        [120, 10, 0],  # Urea
        [18, 46, 0],   # DAP (High P)
        [20, 50, 5],   # DAP
        [0, 0, 60],    # MOP (High K)
        [5, 5, 55],    # MOP
        [19, 19, 19],  # NPK 19-19-19 (Balanced)
        [20, 20, 20]   # NPK
    ])
    
    # Target classes: 0: Urea, 1: DAP, 2: MOP, 3: NPK-19-19-19
    y = np.array([0, 0, 1, 1, 2, 2, 3, 3])
    
    model = DecisionTreeClassifier(max_depth=3)
    model.fit(X, y)
    
    # Ensure models directory exists
    os.makedirs("models", exist_ok=True)
    
    # Serialize model using pickle
    model_path = "models/fertilizer_dt.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
        
    print(f"Fertilizer model serialized successfully to {model_path}")

if __name__ == "__main__":
    train_and_serialize_fertilizer_model()
