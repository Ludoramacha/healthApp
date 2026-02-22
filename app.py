from flask import Flask, jsonify
from flask_cors import CORS
from services.supabase_service import SupabaseService
from dotenv import load_dotenv
import os

# 1. Load your credentials from .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# 2. Initialize your Service
# This happens once when the app starts
db_service = SupabaseService()

@app.route('/api/patient/<rook_id>', methods=['GET'])
def get_patient_dashboard(rook_id):
    print(f"--- Request received for Patient: {rook_id} ---")
    
    # Step A: Find the patient record using that Rook ID string
    patient = db_service.get_patient_by_rook_id(rook_id)
    
    if not patient:
        print(f"Error: No patient found with ID {rook_id}")
        return jsonify({"error": "Patient not found"}), 404

    # Step B: Use the internal UUID to get their history
    patient_uuid = patient['id']
    readings = db_service.get_patient_readings(patient_uuid)
    alerts = db_service.get_patient_alerts(patient_uuid)

    # Step C: Combine and return
    return jsonify({
        "info": {
            "name": patient['name'],
            "email": patient['email'],
            "thresholds": {
                "systolic": patient['systolic_threshold'],
                "diastolic": patient['diastolic_threshold']
            }
        },
        "stats": {
            "total_readings": len(readings),
            "total_alerts": len(alerts)
        },
        "history": readings,
        "active_alerts": alerts
    })

if __name__ == '__main__':
    # Force it to port 5000 and enable debug to see those logs!
    app.run(debug=True, port=5000)