from flask import Blueprint, request, jsonify
from services.supabase_service import SupabaseService
from services.twilio_service import TwilioService
from models import Patient
import uuid

patient_bp = Blueprint('patient', __name__)
supabase_service = SupabaseService()
twilio_service = TwilioService()

@patient_bp.route('/register', methods=['POST'])
def register_patient():
    """Register a new patient"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone_number', 'clinician_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create patient object
        patient = Patient(
            name=data['name'],
            email=data['email'],
            phone_number=data['phone_number'],
            clinician_id=data['clinician_id'],
            systolic_threshold=data.get('systolic_threshold', 160),
            diastolic_threshold=data.get('diastolic_threshold', 100)
        )
        
        # Register in Supabase
        result = supabase_service.register_patient(patient)
        
        if result:
            return jsonify({
                'message': 'Patient registered successfully',
                'patient': result
            }), 201
        else:
            return jsonify({'error': 'Failed to register patient'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@patient_bp.route('/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get patient by ID"""
    try:
        patient = supabase_service.get_patient(patient_id)
        
        if patient:
            return jsonify({
                'message': 'Patient found',
                'patient': patient
            }), 200
        else:
            return jsonify({'error': 'Patient not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@patient_bp.route('/clinician/<clinician_id>', methods=['GET'])
def get_clinician_patients(clinician_id):
    """Get all patients for a clinician"""
    try:
        patients = supabase_service.get_clinician_patients(clinician_id)
        
        return jsonify({
            'message': 'Patients retrieved successfully',
            'count': len(patients),
            'patients': patients
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@patient_bp.route('/<patient_id>/readings', methods=['GET'])
def get_patient_readings(patient_id):
    """Get patient's recent readings"""
    try:
        limit = request.args.get('limit', 10, type=int)
        readings = supabase_service.get_patient_readings(patient_id, limit)
        
        return jsonify({
            'message': 'Readings retrieved successfully',
            'count': len(readings),
            'readings': readings
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@patient_bp.route('/<patient_id>/alerts', methods=['GET'])
def get_patient_alerts(patient_id):
    """Get patient's alerts"""
    try:
        alerts = supabase_service.get_patient_alerts(patient_id)
        
        return jsonify({
            'message': 'Alerts retrieved successfully',
            'count': len(alerts),
            'alerts': alerts
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500