# store/utils.py
from django.conf import settings
from twilio.rest import Client

def send_whatsapp_message(phone_number, message):
    """
    Send WhatsApp message using Twilio API
    """
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f'whatsapp:{phone_number}'
        )
        return True
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")
        return False