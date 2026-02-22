from twilio.rest import Client
import os

class TwilioService:
    def __init__(self):
        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
    
    def send_whatsapp_alert(self, phone_number: str, message: str):
        """Send WhatsApp message alert"""
        try:
            msg = self.client.messages.create(
                from_=f"whatsapp:{self.whatsapp_number}",
                to=f"whatsapp:{phone_number}",
                body=message
            )
            print(f"WhatsApp sent: {msg.sid}")
            return True
        except Exception as e:
            print(f"Error sending WhatsApp: {e}")
            return False