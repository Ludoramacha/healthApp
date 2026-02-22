import requests
import json

BASE_URL = "http://localhost:5000"

def test_rook_flow():
    """Test the complete Rook integration flow"""
    
    print("=" * 50)
    print("ROOK INTEGRATION TEST")
    print("=" * 50)
    
    # Step 1: Register a patient first
    print("\n1. Registering a test patient...")
    patient_data = {
        "name": "Test Patient",
        "email": "test@example.com",
        "phone_number": "+1234567890",
        "clinician_id": "doc-123"
    }
    
    response = requests.post(f"{BASE_URL}/api/patient/register", json=patient_data)
    print(f"Status: {response.status_code}")
    patient_response = response.json()
    print(json.dumps(patient_response, indent=2))
    
    if response.status_code != 201:
        print("Failed to register patient. Stopping test.")
        return
    
    patient_id = patient_response['patient']['id']
    print(f"\n✓ Patient registered with ID: {patient_id}")
    
    # Step 2: Initialize Rook for the patient
    print("\n2. Initializing Rook for patient...")
    response = requests.post(f"{BASE_URL}/api/rook/initialize/{patient_id}")
    print(f"Status: {response.status_code}")
    rook_response = response.json()
    print(json.dumps(rook_response, indent=2))
    
    if response.status_code != 200:
        print("Failed to initialize Rook. Stopping test.")
        return
    
    rook_user_id = rook_response.get('rook_user_id')
    connection_code = rook_response.get('connection_code')
    
    print(f"\n✓ Rook initialized!")
    print(f"  Rook User ID: {rook_user_id}")
    print(f"  Connection Code: {connection_code}")
    print(f"  Instructions: {rook_response.get('instructions')}")
    
    # Step 3: Get connection code
    print("\n3. Retrieving connection code...")
    response = requests.get(f"{BASE_URL}/api/rook/connection-code/{rook_user_id}")
    print(f"Status: {response.status_code}")
    code_response = response.json()
    print(json.dumps(code_response, indent=2))
    
    # Step 4: Trigger data sync
    print("\n4. Triggering data sync...")
    response = requests.post(f"{BASE_URL}/api/rook/sync/{rook_user_id}")
    print(f"Status: {response.status_code}")
    sync_response = response.json()
    print(json.dumps(sync_response, indent=2))
    
    # Step 5: Get latest reading (may be empty if no device connected yet)
    print("\n5. Retrieving latest reading...")
    response = requests.get(f"{BASE_URL}/api/rook/latest-reading/{rook_user_id}")
    print(f"Status: {response.status_code}")
    reading_response = response.json()
    print(json.dumps(reading_response, indent=2))
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)
    print(f"\nNext Steps:")
    print(f"1. Use the connection code to connect a health device")
    print(f"2. Sync data from your device")
    print(f"3. Check for blood pressure readings")

if __name__ == "__main__":
    test_rook_flow()