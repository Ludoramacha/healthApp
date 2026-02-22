from flask import Blueprint, request, jsonify
from services.supabase_service import SupabaseService
from services.twilio_service import TwilioService
from models import Reading, Alert
from datetime import datetime

reading_bp = Blueprint('reading', __name__)
supabase_service = SupabaseService()
twilio_service = TwilioService()

@reading_bp.route('/add', methods=['POST'])
def add_reading():
    """Add a new blood pressure reading"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['patient_id', 'systolic', 'diastolic', 'heart_rate']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get patient to check thresholds
        patient = supabase_service.get_patient(data['patient_id'])
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Create reading object
        reading = Reading(
            patient_id=data['patient_id'],
            systolic=data['systolic'],
            diastolic=data['diastolic'],
            heart_rate=data['heart_rate'],
            source=data.get('source', 'manual')
        )
        
        # Add reading to Supabase
        result = supabase_service.add_reading(reading)
        
        if result:
            # Check if reading exceeds thresholds
            if (reading.systolic > patient['systolic_threshold'] or 
                reading.diastolic > patient['diastolic_threshold']):
                
                # Process alert
                alert_created = process_alert(patient, result)
            
            return jsonify({
                'message': 'Reading added successfully',
                'reading': result,
                'alert_triggered': (reading.systolic > patient['systolic_threshold'] or 
                                   reading.diastolic > patient['diastolic_threshold'])
            }), 201
        else:
            return jsonify({'error': 'Failed to add reading'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def process_alert(patient, reading):
    """Create alert and send notifications"""
    try:
        # Determine alert type
        if reading['systolic'] > patient['systolic_threshold']:
            alert_type = 'high_systolic'
        else:
            alert_type = 'high_diastolic'
        
        # Create alert message
        alert_message = (
            f"🚨 High Blood Pressure Alert!\n"
            f"Patient: {patient['name']}\n"
            f"Systolic: {reading['systolic']} mmHg\n"
            f"Diastolic: {reading['diastolic']} mmHg\n"
            f"Heart Rate: {reading['heart_rate']} bpm\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # Create alert in database
        alert = Alert(
            patient_id=patient['id'],
            reading_id=reading['id'],
            alert_type=alert_type,
            message=alert_message
        )
        
        alert_result = supabase_service.add_alert(alert)
        
        # Send WhatsApp notification
        twilio_service.send_whatsapp_alert(patient['phone_number'], alert_message)
        
        print(f"Alert created for patient {patient['id']}")
        return True
    
    except Exception as e:
        print(f"Error processing alert: {e}")
        return False