from flask import Blueprint, request, jsonify
from services.supabase_service import SupabaseService
from services.twilio_service import TwilioService
from models import Reading, Alert
from datetime import datetime

webhook_bp = Blueprint('webhook', __name__)
supabase_service = SupabaseService()
twilio_service = TwilioService()

@webhook_bp.route('/rook', methods=['POST'])
def receive_rook_data():
    """Webhook endpoint to receive health data from Rook"""
    try:
        data = request.get_json()
        
        print(f"Rook webhook received: {data}")
        
        # Extract data from webhook payload
        rook_user_id = data.get('user_id')
        health_data = data.get('data', {})
        
        # Find patient by rook_user_id
        # Note: You'll need to implement a method to search by rook_user_id
        # For now, we'll assume it comes in the payload
        patient_id = data.get('patient_id')
        
        if not patient_id:
            return jsonify({'error': 'Patient ID not found'}), 400
        
        patient = supabase_service.get_patient(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Extract blood pressure reading from Rook data
        blood_pressure = health_data.get('blood_pressure', {})
        
        if not blood_pressure:
            return jsonify({'error': 'No blood pressure data in payload'}), 400
        
        systolic = blood_pressure.get('systolic')
        diastolic = blood_pressure.get('diastolic')
        heart_rate = blood_pressure.get('heart_rate', 0)
        
        if systolic is None or diastolic is None:
            return jsonify({'error': 'Missing systolic or diastolic values'}), 400
        
        # Create reading object
        reading = Reading(
            patient_id=patient_id,
            systolic=systolic,
            diastolic=diastolic,
            heart_rate=heart_rate,
            source='rook'
        )
        
        # Add reading to Supabase
        result = supabase_service.add_reading(reading)
        
        if result:
            # Check if reading exceeds thresholds
            if (systolic > patient['systolic_threshold'] or 
                diastolic > patient['diastolic_threshold']):
                
                process_alert(patient, result)
            
            return jsonify({
                'message': 'Reading processed successfully',
                'reading_id': result['id'],
                'alert_triggered': (systolic > patient['systolic_threshold'] or 
                                   diastolic > patient['diastolic_threshold'])
            }), 200
        else:
            return jsonify({'error': 'Failed to process reading'}), 500
    
    except Exception as e:
        print(f"Webhook error: {e}")
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


@webhook_bp.route('/health', methods=['GET'])
def webhook_health():
    """Health check endpoint for webhooks"""
    return jsonify({'status': 'webhook service is running'}), 200