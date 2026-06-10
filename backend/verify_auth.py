import sys
import httpx

BASE_URL = "http://localhost:8000/api/v1"

def run_tests():
    print("=== Starting Auth & RBAC Verification Tests ===")

    # 1. Test Admin Signup Block
    print("\n1. Testing Admin Signup Block (Should fail with 400)...")
    payload = {
        "email": "admin-test@agroguide.com",
        "password": "securepassword123",
        "full_name": "Test Admin",
        "role": "admin"
    }
    r = httpx.post(f"{BASE_URL}/auth/register", json=payload)
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 400, "Admin signup should be blocked publicly."
    print("Success: Admin signup blocked.")

    # 2. Test Customer Signup
    print("\n2. Testing Customer Signup...")
    payload = {
        "email": "customer-test@agroguide.com",
        "password": "customerpassword123",
        "full_name": "Test Customer",
        "role": "customer"
    }
    r = httpx.post(f"{BASE_URL}/auth/register", json=payload)
    print(f"Status: {r.status_code}")
    assert r.status_code in [201, 400], "Customer signup failed."
    print("Success: Customer registered or already existed.")

    # 3. Test Farmer Signup
    print("\n3. Testing Farmer Signup...")
    payload = {
        "email": "farmer-test@agroguide.com",
        "password": "farmerpassword123",
        "full_name": "Test Farmer",
        "role": "farmer"
    }
    r = httpx.post(f"{BASE_URL}/auth/register", json=payload)
    print(f"Status: {r.status_code}")
    assert r.status_code in [201, 400], "Farmer signup failed."
    print("Success: Farmer registered or already existed.")

    # 4. Test Customer Login
    print("\n4. Testing Customer Login (token-json)...")
    payload = {
        "email": "customer-test@agroguide.com",
        "password": "customerpassword123"
    }
    r = httpx.post(f"{BASE_URL}/auth/token-json", json=payload)
    print(f"Status: {r.status_code}")
    assert r.status_code == 200, "Login failed."
    tokens = r.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    print("Success: Customer logged in. Access and Refresh tokens obtained.")

    # 5. Test GET /auth/me
    print("\n5. Testing /auth/me (Current User Profile)...")
    headers = {"Authorization": f"Bearer {access_token}"}
    r = httpx.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status: {r.status_code}, Profile: {r.text}")
    assert r.status_code == 200
    assert r.json()["role"] == "customer"
    print("Success: /auth/me successfully returned customer context.")

    # 6. Test Customer accessing Farmer protected route
    print("\n6. Testing Customer accessing Farmer route (Should fail with 403)...")
    r = httpx.get(f"{BASE_URL}/auth/farmer-only-test", headers=headers)
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 403
    print("Success: Customer blocked from Farmer route.")

    # 7. Test Farmer Login and accessing Farmer protected route
    print("\n7. Testing Farmer Login and access to Farmer route...")
    payload = {
        "email": "farmer-test@agroguide.com",
        "password": "farmerpassword123"
    }
    r = httpx.post(f"{BASE_URL}/auth/token-json", json=payload)
    farmer_access_token = r.json()["access_token"]
    farmer_headers = {"Authorization": f"Bearer {farmer_access_token}"}
    r = httpx.get(f"{BASE_URL}/auth/farmer-only-test", headers=farmer_headers)
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 200
    print("Success: Farmer authorized to access Farmer route.")

    # 8. Test Refresh Token exchange
    print("\n8. Testing Token Refresh...")
    payload = {"refresh_token": refresh_token}
    r = httpx.post(f"{BASE_URL}/auth/refresh", json=payload)
    print(f"Status: {r.status_code}")
    assert r.status_code == 200
    new_access_token = r.json()["access_token"]
    print("Success: New access token generated from refresh token.")

    # 9. Test Logout (Revocation)
    print("\n9. Testing Logout (Revocation)...")
    r = httpx.post(f"{BASE_URL}/auth/logout", json=payload, headers=headers)
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 200
    print("Success: Logout returned success status.")

    # 10. Test Refresh after Logout (Should fail with 401)
    print("\n10. Testing Refresh with Revoked Token (Should fail with 401)...")
    r = httpx.post(f"{BASE_URL}/auth/refresh", json=payload)
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 401
    print("Success: Revoked refresh token rejected.")

    print("\n=== All Authentication & RBAC Verification Tests Passed! ===")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"Test Execution Failed: {e}", file=sys.stderr)
        sys.exit(1)
