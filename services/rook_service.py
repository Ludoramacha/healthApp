import requests
import os
import json
from datetime import datetime, timedelta

class RookIntegrationService:
    def __init__(self):
        self.client_id = os.getenv("ROOK_CLIENT_ID")
        self.client_secret = os.getenv("ROOK_CLIENT_SECRET")
        self.base_url = os.getenv("ROOK_BASE_URL", "https://api.rook.co")
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self):
        """Get OAuth access token from Rook"""
        try:
            # Check if token is still valid
            if self.access_token and self.token_expires_at > datetime.now():
                return self.access_token
            
            # Request new token
            url = f"{self.base_url}/auth/token"
            payload = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials"
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            return self.access_token
        
        except Exception as e:
            print(f"Error getting Rook access token: {e}")
            return None
    
    def create_user(self, patient_id: str, email: str):
        """Create a Rook user and get their code for device connection"""
        try:
            token = self.get_access_token()
            if not token:
                return None
            
            url = f"{self.base_url}/users"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            payload = {
                "external_id": patient_id,
                "email": email
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            rook_user_id = data.get("id")
            connection_code = data.get("connection_code")
            
            print(f"Rook user created: {rook_user_id}")
            return {
                "rook_user_id": rook_user_id,
                "connection_code": connection_code
            }
        
        except Exception as e:
            print(f"Error creating Rook user: {e}")
            return None
    
    def get_connection_code(self, rook_user_id: str):
        """Get connection code for a Rook user to connect devices"""
        try:
            token = self.get_access_token()
            if not token:
                return None
            
            url = f"{self.base_url}/users/{rook_user_id}/connection-code"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            connection_code = data.get("connection_code")
            
            return connection_code
        
        except Exception as e:
            print(f"Error getting connection code: {e}")
            return None
    
    def get_health_data(self, rook_user_id: str, data_type: str = "blood_pressure"):
        """Get health data for a specific user"""
        try:
            token = self.get_access_token()
            if not token:
                return None
            
            url = f"{self.base_url}/users/{rook_user_id}/data/{data_type}"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data
        
        except Exception as e:
            print(f"Error getting health data from Rook: {e}")
            return None
    
    def get_latest_reading(self, rook_user_id: str):
        """Get latest blood pressure reading from Rook"""
        try:
            data = self.get_health_data(rook_user_id, "blood_pressure")
            
            if data and data.get("readings"):
                readings = data.get("readings", [])
                if readings:
                    latest = readings[0]  # Assuming first is most recent
                    return {
                        "systolic": latest.get("systolic"),
                        "diastolic": latest.get("diastolic"),
                        "heart_rate": latest.get("heart_rate"),
                        "timestamp": latest.get("timestamp")
                    }
            
            return None
        
        except Exception as e:
            print(f"Error getting latest reading: {e}")
            return None
    
    def sync_user_data(self, rook_user_id: str):
        """Trigger a sync for user's health data"""
        try:
            token = self.get_access_token()
            if not token:
                return False
            
            url = f"{self.base_url}/users/{rook_user_id}/sync"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            
            print(f"Sync triggered for user {rook_user_id}")
            return True
        
        except Exception as e:
            print(f"Error triggering sync: {e}")
            return False