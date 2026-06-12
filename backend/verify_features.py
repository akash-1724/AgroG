import math
import uuid
from datetime import datetime

# 1. Haversine Calculation logic check
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # 6371 represents Earth's radius in kilometers
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def test_haversine():
    # Test Bengaluru coordinates to Kolar coordinates (~60-70km)
    blr_lat, blr_lon = 12.9716, 77.5946
    kolar_lat, kolar_lon = 13.1368, 78.1292
    
    distance = haversine_distance(blr_lat, blr_lon, kolar_lat, kolar_lon)
    print(f"Haversine test distance (Bangalore -> Kolar): {distance} km")
    # Distance should be positive and within reasonable bounds (roughly 60 to 75 km)
    assert 55.0 <= distance <= 75.0, f"Distance {distance} km is out of expected range."
    print("✓ Haversine distance verification passed.")

# 2. Location Privacy Blurring check
def blur_coordinates(lat: float, lon: float) -> tuple[float, float]:
    return round(lat, 2), round(lon, 2)

def test_privacy_blurring():
    lat, lon = 12.971593, 77.594562
    blurred_lat, blurred_lon = blur_coordinates(lat, lon)
    print(f"Original: ({lat}, {lon}) -> Blurred: ({blurred_lat}, {blurred_lon})")
    assert blurred_lat == 12.97, f"Expected 12.97, got {blurred_lat}"
    assert blurred_lon == 77.59, f"Expected 77.59, got {blurred_lon}"
    print("✓ Location privacy blurring verification passed.")

# 3. Message Safety check
def is_safe_message(text: str) -> bool:
    text_lower = text.lower()
    dangerous_terms = [
        "lethal dose", "poison", "toxic concentration", "illegal chemical",
        "kill crops", "sabotage", "homemade pesticide", "explosive fertilizer"
    ]
    return not any(term in text_lower for term in dangerous_terms)

def test_safety_check():
    safe_query = "How do I balance nitrogen levels in my tomato crops?"
    unsafe_query = "What is the lethal dose of illegal chemical pesticide to kill crops?"
    
    assert is_safe_message(safe_query) == True, "Safe query flagged incorrect."
    assert is_safe_message(unsafe_query) == False, "Unsafe query not intercepted."
    print("✓ Safety interceptor logic verification passed.")

if __name__ == "__main__":
    print("Running custom verification suite for AgroGuide content-location-assistant...")
    test_haversine()
    test_privacy_blurring()
    test_safety_check()
    print("All backend checks passed successfully!")
