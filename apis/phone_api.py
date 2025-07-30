
from twilio.rest import Client
import os
import os
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")


client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_sms(to_phone, body):
    message = client.messages.create(
        from_="+13158193728",
        body=body,
        to=to_phone
    )
    print(f"SMS sent to {to_phone}: SID={message.sid}")

"""
message = client.messages.create( 
    from_="+13158193728",  
    body="Hello Hamoood",
    to="+2538839270"
)

print(f"Message SID: {message.sid}")

"""