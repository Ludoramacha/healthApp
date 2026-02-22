import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Firebase
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
    
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_WHATSAPP_NUMBER = os.getenv("+26773070695")
    
    # Rook
    ROOK_BASE_URL = os.getenv("ROOK_BASE_URL", "https://api.rook.co")
    ROOK_CLIENT_ID = os.getenv("179ee24c-ac6f-4d1d-a3ce-0b128f53361c")
    ROOK_CLIENT_SECRET = os.getenv("ZGsypZrhEoaam5tmiWEcBUv3Zsvq-Kvjy9QRK")
    
    # Flask
    FLASK_ENV = os.getenv("FLASK_ENV", "development")