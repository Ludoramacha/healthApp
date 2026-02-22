from flask import Blueprint, request, jsonify
from services.rook_service import RookIntegrationService
from services.supabase_service import SupabaseService

rook_bp = Blueprint('rook', __name__)
rook_service = RookIntegrationService()
supabase_service = SupabaseService()

@rook_bp.route('/initialize/<patient_id>', methods=['POST'])
def initialize_rook(patient_id):
    """Initialize Rook for a patient and get connection code"""
    try:
        # Get patient details
        patient = supabase_service.get_patient(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Create Rook user
        rook_data = rook_service.create_user(patient_id, patient['email'])
        if not rook_data:
            return jsonify({'error': 'Failed to initialize Rook'}), 500
        
        # Update patient with rook_user_id
        supabase_service.update_patient_rook_id(patient_id, rook_data['rook_user_id'])
        
        return jsonify({
            'message': 'Rook initialized successfully',
            'patient_id': patient_id,
            'rook_user_id': rook_data['rook_user_id'],
            'connection_code': rook_data['connection_code'],
            'instructions': 'Use this connection code to connect your health device/app in the Rook app'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rook_bp.route('/connection-code/<rook_user_id>', methods=['GET'])
def get_connection_code(rook_user_id):
    """Get connection code for a Rook user"""
    try:
        code = rook_service.get_connection_code(rook_user_id)
        
        if code:
            return jsonify({
                'connection_code': code,
                'instructions': 'Use this code to connect your health device'
            }), 200
        else:
            return jsonify({'error': 'Failed to get connection code'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rook_bp.route('/sync/<rook_user_id>', methods=['POST'])
def sync_data(rook_user_id):
    """Trigger data sync for a Rook user"""
    try:
        success = rook_service.sync_user_data(rook_user_id)
        
        if success:
            return jsonify({
                'message': 'Data sync triggered successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to trigger sync'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rook_bp.route('/latest-reading/<rook_user_id>', methods=['GET'])
def get_latest_reading(rook_user_id):
    """Get latest blood pressure reading from Rook"""
    try:
        reading = rook_service.get_latest_reading(rook_user_id)
        
        if reading:
            return jsonify({
                'message': 'Latest reading retrieved',
                'reading': reading
            }), 200
        else:
            return jsonify({'error': 'No readings found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rook_bp.route('/webhook', methods=['POST'])
def rook_webhook():
    """Webhook to receive real-time data from Rook"""
    try:
        data = request.get_json()
        print(f"Rook webhook received: {data}")
        
        rook_user_id = data.get('user_id')
        event_type = data.get('event_type')
        payload = data.get('payload', {})
        
        if event_type == 'blood_pressure_updated':
            # Get patient by rook_user_id
            patient = supabase_service.get_patient_by_rook_id(rook_user_id)
            if not patient:
                return jsonify({'error': 'Patient not found'}), 404
            
            # Extract blood pressure data
            blood_pressure = payload.get('blood_pressure', {})
            systolic = blood_pressure.get('systolic')
            diastolic = blood_pressure.get('diastolic')
            heart_rate = blood_pressure.get('heart_rate', 0)
            
            if systolic and diastolic:
                # Create reading from Rook data
                from models import Reading, Alert
                from datetime import datetime
                
                reading = Reading(
                    patient_id=patient['id'],
                    systolic=systolic,
                    diastolic=diastolic,
                    heart_rate=heart_rate,
                    source='rook'
                )
                
                result = supabase_service.add_reading(reading)
                
                if result:
                    # Check thresholds and create alert if needed
                    if (systolic > patient['systolic_threshold'] or 
                        diastolic > patient['diastolic_threshold']):
                        
                        from services.twilio_service import TwilioService
                        twilio_service = TwilioService()
                        
                        alert_type = 'high_systolic' if systolic > patient['systolic_threshold'] else 'high_diastolic'
                        alert_message = (
                            f"🚨 High Blood Pressure Alert!\n"
                            f"Patient: {patient['name']}\n"
                            f"Systolic: {systolic} mmHg\n"
                            f"Diastolic: {diastolic} mmHg\n"
                            f"Heart Rate: {heart_rate} bpm\n"
                            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                        
                        alert = Alert(
                            patient_id=patient['id'],
                            reading_id=result['id'],
                            alert_type=alert_type,
                            message=alert_message
                        )
                        
                        supabase_service.add_alert(alert)
                        twilio_service.send_whatsapp_alert(patient['phone_number'], alert_message)
                        
                        print(f"Alert sent to {patient['name']}")
        
        elif event_type == 'user_disconnected':
            print(f"User {rook_user_id} disconnected from Rook")
        
        return jsonify({'message': 'Webhook processed'}), 200
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500