import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("COMPLETE WELLNESS WATCH FLOW TEST")
print("=" * 60)

# 1. Register Patient
print("\n1️⃣  Registering patient...")
patient_data = {
    "name": "John Smith",
    "email": "john.smith@example.com",
    "phone_number": "+1234567890",
    "clinician_id": "dr-johnson",
    "systolic_threshold": 140,
    "diastolic_threshold": 90
}
response = requests.post(f"{BASE_URL}/api/patient/register", json=patient_data)
patient = response.json()['patient']
patient_id = patient['id']
print(f"✓ Patient registered: {patient['name']} (ID: {patient_id})")

# 2. Initialize Rook
print("\n2️⃣  Initializing Rook...")
print(">>> WEBHOOK ROUTE HIT! <<<") # If you don't see this, the port is wrong.
response = requests.post(f"{BASE_URL}/api/rook/initialize/{patient_id}")
rook_data = response.json()
rook_user_id = rook_data['rook_user_id']
print(f"✓ Rook initialized")
print(f"  - Rook User ID: {rook_user_id}")
print(f"  - Connection Code: {rook_data['connection_code']}")

# 3. Verify Patient has Rook ID
print("\n3️⃣  Checking if patient was updated with Rook ID...")
response = requests.get(f"{BASE_URL}/api/patient/{patient_id}")
updated_patient = response.json()['patient']
print(f"✓ Patient Rook ID: {updated_patient['rook_user_id']}")

# 4. Add a Manual Reading (simulate blood pressure device)
print("\n4️⃣  Adding blood pressure reading...")
reading_data = {
    "patient_id": patient_id,
    "systolic": 145,
    "diastolic": 95,
    "heart_rate": 78,
    "source": "manual"
}
response = requests.post(f"{BASE_URL}/api/reading/add", json=reading_data)
reading_result = response.json()
print(f"✓ Reading added")
print(f"  - Alert triggered: {reading_result['alert_triggered']}")

# 5. Get Patient Readings
print("\n5️⃣  Retrieving patient readings...")
response = requests.get(f"{BASE_URL}/api/patient/{patient_id}/readings")
readings = response.json()['readings']
print(f"✓ Retrieved {len(readings)} reading(s)")
for r in readings:
    print(f"  - {r['systolic']}/{r['diastolic']} mmHg, HR: {r['heart_rate']} bpm")

# 6. Get Alerts
print("\n6️⃣  Checking alerts...")
response = requests.get(f"{BASE_URL}/api/patient/{patient_id}/alerts")
alerts = response.json()['alerts']
print(f"✓ Retrieved {len(alerts)} alert(s)")
for a in alerts:
    print(f"  - {a['alert_type']}: {a['message'][:50]}...")

print("\n" + "=" * 60)
print("✅ FULL FLOW TEST COMPLETE!")
print("=" * 60)