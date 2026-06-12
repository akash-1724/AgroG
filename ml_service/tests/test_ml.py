import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from ml_service.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "demo_mode_active" in data

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "demo_mode" in data

def test_model_status():
    response = client.get("/model-status")
    assert response.status_code == 200
    data = response.json()
    assert "demo_mode" in data
    assert "models" in data
    assert "crop_recommendation" in data["models"]
    assert "fertilizer_recommendation" in data["models"]
    assert "disease_detection" in data["models"]

def test_recommend_crop_valid():
    payload = {
        "nitrogen": 50.0,
        "phosphorus": 50.0,
        "potassium": 50.0,
        "ph": 6.5,
        "temperature": 25.0,
        "humidity": 80.0,
        "rainfall": 150.0
    }
    response = client.post("/recommendations/crop", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "model_status" in data
    assert "disclaimer" in data
    assert "limitations" in data

def test_recommend_crop_invalid():
    # Test nitrogen out of bounds (> 200)
    payload = {
        "nitrogen": 250.0,
        "phosphorus": 50.0,
        "potassium": 50.0,
        "ph": 6.5,
        "temperature": 25.0,
        "humidity": 80.0,
        "rainfall": 150.0
    }
    response = client.post("/recommendations/crop", json=payload)
    assert response.status_code == 422

    # Test ph out of bounds (< 3.5)
    payload["nitrogen"] = 50.0
    payload["ph"] = 2.0
    response = client.post("/recommendations/crop", json=payload)
    assert response.status_code == 422

def test_recommend_fertilizer_valid():
    payload = {
        "nitrogen": 45.0,
        "phosphorus": 45.0,
        "potassium": 45.0
    }
    response = client.post("/recommendations/fertilizer", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommended_fertilizer" in data
    assert "model_status" in data
    assert "guideline" in data
    assert "disclaimer" in data

def test_recommend_fertilizer_invalid():
    payload = {
        "nitrogen": -10.0,
        "phosphorus": 45.0,
        "potassium": 45.0
    }
    response = client.post("/recommendations/fertilizer", json=payload)
    assert response.status_code == 422

def test_detect_disease_valid_image():
    # Generate a dummy image using PIL
    img = Image.new("RGB", (100, 100), color="green")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    
    files = {"file": ("test.png", img_byte_arr, "image/png")}
    response = client.post("/disease/detect", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_disease" in data
    assert "confidence" in data
    assert "remedy" in data
    assert "model_status" in data

def test_detect_disease_invalid_type():
    files = {"file": ("test.txt", io.BytesIO(b"dummy text"), "text/plain")}
    response = client.post("/disease/detect", files=files)
    assert response.status_code == 400
    assert "Only JPEG, JPG and PNG are supported" in response.json()["detail"]

def test_detect_disease_too_large():
    # Use a dummy content of 6MB to test 5MB limit
    large_content = b"a" * (6 * 1024 * 1024)
    files = {"file": ("test.png", io.BytesIO(large_content), "image/png")}
    response = client.post("/disease/detect", files=files)
    assert response.status_code == 413
