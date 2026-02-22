from datetime import datetime
from typing import Optional

class Patient:
    def __init__(self, name: str, email: str, phone_number: str, 
                 clinician_id: str, systolic_threshold: int = 160, 
                 diastolic_threshold: int = 100):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.clinician_id = clinician_id
        self.rook_user_id = None
        self.systolic_threshold = systolic_threshold
        self.diastolic_threshold = diastolic_threshold
    
    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'phone_number': self.phone_number,
            'clinician_id': self.clinician_id,
            'rook_user_id': self.rook_user_id,
            'systolic_threshold': self.systolic_threshold,
            'diastolic_threshold': self.diastolic_threshold,
        }


class Reading:
    def __init__(self, patient_id: str, systolic: int, diastolic: int, 
                 heart_rate: int, source: str = "manual"):
        self.patient_id = patient_id
        self.systolic = systolic
        self.diastolic = diastolic
        self.heart_rate = heart_rate
        self.source = source
    
    def to_dict(self):
        return {
            'patient_id': self.patient_id,
            'systolic': self.systolic,
            'diastolic': self.diastolic,
            'heart_rate': self.heart_rate,
            'source': self.source,
        }


class Alert:
    def __init__(self, patient_id: str, reading_id: str, alert_type: str, message: str):
        self.patient_id = patient_id
        self.reading_id = reading_id
        self.alert_type = alert_type
        self.message = message
        self.resolved = False
    
    def to_dict(self):
        return {
            'patient_id': self.patient_id,
            'reading_id': self.reading_id,
            'alert_type': self.alert_type,
            'message': self.message,
            'resolved': self.resolved,
        }