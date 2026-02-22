from supabase import create_client, Client
import os
from models import Patient, Reading, Alert
import uuid

class SupabaseService:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    
    # Patient Operations
    def register_patient(self, patient: Patient):
        """Register a new patient"""
        try:
            patient_data = patient.to_dict()
            patient_data['id'] = str(uuid.uuid4())
            response = self.supabase.table("patients").insert(patient_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error registering patient: {e}")
            return None
    
    def get_patient(self, patient_id: str):
        """Get patient by ID"""
        try:
            response = self.supabase.table("patients").select("*").eq("id", patient_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching patient: {e}")
            return None
    
    def get_clinician_patients(self, clinician_id: str):
        """Get all patients for a clinician"""
        try:
            response = self.supabase.table("patients").select("*").eq("clinician_id", clinician_id).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching clinician patients: {e}")
            return []
    
    # Reading Operations
    def add_reading(self, reading: Reading):
        """Add a new blood pressure reading"""
        try:
            reading_data = reading.to_dict()
            reading_data['id'] = str(uuid.uuid4())
            response = self.supabase.table("readings").insert(reading_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error adding reading: {e}")
            return None
    
    def get_patient_readings(self, patient_id: str, limit: int = 10):
        """Get recent readings for a patient"""
        try:
            response = self.supabase.table("readings").select("*").eq("patient_id", patient_id).order("created_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching readings: {e}")
            return []
    
    # Alert Operations
    def add_alert(self, alert: Alert):
        """Create a new alert"""
        try:
            alert_data = alert.to_dict()
            alert_data['id'] = str(uuid.uuid4())
            response = self.supabase.table("alerts").insert(alert_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error adding alert: {e}")
            return None
    
    def get_patient_alerts(self, patient_id: str):
        """Get all alerts for a patient"""
        try:
            response = self.supabase.table("alerts").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching alerts: {e}")
            return []      
        
    def get_patient_by_rook_id(self, rook_user_id: str):
        try:
            print(f"DEBUG: Searching for rook_user_id: '{rook_user_id}'")
            
            response = self.supabase.table("patients") \
                .select("*") \
                .eq("rook_user_id", rook_user_id) \
                .execute()

            if not response.data:
                print(f"DEBUG: Query successful but NO MATCH found for '{rook_user_id}'")
                return None
                
            print(f"DEBUG: Match found! Patient Name: {response.data[0].get('name')}")
            return response.data[0]
        except Exception as e:
            print(f"DEBUG: Supabase query crashed! Error: {e}")
            return None

    def update_patient_rook_id(self, patient_id: str, rook_user_id: str):
        """Update patient's Rook user ID"""
        try:
            response = self.supabase.table("patients").update(
                {"rook_user_id": rook_user_id}
            ).eq("id", patient_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating patient Rook ID: {e}")
            return None    