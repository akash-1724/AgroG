import sys
import httpx

BASE_URL = "http://localhost:8000/api/v1"

def test_marketplace():
    print("=== Starting Marketplace & Orders Verification Tests ===")

    # Setup standard logins
    print("\nLog in users...")
    # Farmer login
    r = httpx.post(f"{BASE_URL}/auth/token-json", json={"email": "farmer-test@agroguide.com", "password": "farmerpassword123"})
    assert r.status_code == 200, "Farmer login failed"
    farmer_token = r.json()["access_token"]
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}

    # Customer login
    r = httpx.post(f"{BASE_URL}/auth/token-json", json={"email": "customer-test@agroguide.com", "password": "customerpassword123"})
    assert r.status_code == 200, "Customer login failed"
    customer_token = r.json()["access_token"]
    customer_headers = {"Authorization": f"Bearer {customer_token}"}

    # 1. Farmer creates listing
    print("\n1. Testing Listing Creation (Farmer)...")
    payload = {
        "title": "Organic Tomatoes",
        "description": "Fresh vine-ripened organic tomatoes.",
        "price_per_unit": 2.50,
        "unit": "kg",
        "available_quantity": 100,
        "category": "Vegetables"
    }
    r = httpx.post(f"{BASE_URL}/marketplace/listings", json=payload, headers=farmer_headers)
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 201
    listing_id = r.json()["id"]
    print("Success: Listing created.")

    # 2. Customer lists and searches listings
    print("\n2. Testing Listings Search & Filters...")
    r = httpx.get(f"{BASE_URL}/marketplace/?search=Tomatoes&category=Vegetables", headers=customer_headers)
    print(f"Status: {r.status_code}")
    assert r.status_code == 200
    assert len(r.json()) > 0
    print("Success: Listing found via search filters.")

    # 3. Customer places order (Stock validation & deduction check)
    print("\n3. Testing Order Placement with Stock Validation...")
    order_payload = {
        "items": [
            {
                "crop_listing_id": listing_id,
                "quantity": 10
            }
        ]
    }
    r = httpx.post(f"{BASE_URL}/marketplace/orders", json=order_payload, headers=customer_headers)
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 201
    order_id = r.json()["id"]
    print("Success: Order placed.")

    # Check listing stock is reduced
    r = httpx.get(f"{BASE_URL}/marketplace/listings/{listing_id}")
    assert r.json()["available_quantity"] == 90, "Stock was not deducted correctly"
    print("Success: Stock deducted transaction-safely.")

    # 4. Out of stock order test
    print("\n4. Testing Insufficient Stock Order Block (Should fail with 400)...")
    bad_order_payload = {
        "items": [
            {
                "crop_listing_id": listing_id,
                "quantity": 95
            }
        ]
    }
    r = httpx.post(f"{BASE_URL}/marketplace/orders", json=bad_order_payload, headers=customer_headers)
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 400
    print("Success: Over-order blocked successfully.")

    # 5. Non-owner updates listing check (Should fail with 403)
    print("\n5. Testing Unauthorized Listing Update Block (Should fail with 403)...")
    r = httpx.put(f"{BASE_URL}/marketplace/listings/{listing_id}", json={"title": "Stolen Tomatoes"}, headers=customer_headers)
    print(f"Status: {r.status_code}")
    assert r.status_code == 403
    print("Success: Unauthorized edit blocked.")

    # 6. Order Status Transitions & Stock recovery on cancellation
    print("\n6. Testing Order Status Transitions & Stock recovery on cancellation...")
    # Customer cancels own pending order
    cancel_payload = {"status": "cancelled"}
    r = httpx.patch(f"{BASE_URL}/marketplace/orders/{order_id}", json=cancel_payload, headers=customer_headers)
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 200
    print("Success: Order cancelled successfully.")

    # Check stock restored
    r = httpx.get(f"{BASE_URL}/marketplace/listings/{listing_id}")
    assert r.json()["available_quantity"] == 100, "Stock was not restored correctly"
    print("Success: Stock restored fully upon cancellation.")

    # 7. Customer tries invalid status transition (cancelled -> accepted, should fail with 400)
    print("\n7. Testing Invalid Transition Block (Should fail with 400)...")
    r = httpx.patch(f"{BASE_URL}/marketplace/orders/{order_id}", json={"status": "accepted"}, headers=customer_headers)
    print(f"Status: {r.status_code}")
    assert r.status_code == 400
    print("Success: Transition from terminal state blocked.")

    print("\n=== All Marketplace & Order Verification Tests Passed! ===")

if __name__ == "__main__":
    try:
        test_marketplace()
    except Exception as e:
        print(f"Test Execution Failed: {e}", file=sys.stderr)
        sys.exit(1)
