"""
from twilio.rest import Client

# Your Account SID and Auth Token from twilio.com/console
account_sid = "AC481ea9e386f8f2d93d8511d3397d586b"
auth_token = "1268ce8fbd203184c254fdecfa206310"
client = Client(account_sid, auth_token)

# Send SMS
message = client.messages.create(
    body="Hello! This is a reminder from Near Near me that the event xyz you saved is happening in xy hours and is happening at xyz",
    from_="+18777804236",  # Your Twilio number
    to="+12538839270"      # User's phone number
)

print(f"Message sent! SID: {message.sid}")
"""
"""
from twilio.rest import Client
account_sid = 'AC481ea9e386f8f2d93d8511d3397d586b'
auth_token = '1268ce8fbd203184c254fdecfa206310'
client = Client(account_sid, auth_token)
message = client.messages.create(
  from_='+19388678241',
  body='message',
  to='+12538839270'
)
print(message.sid)
"""

from twilio.rest import Client
account_sid = 'AC481ea9e386f8f2d93d8511d3397d586b'
auth_token = '1268ce8fbd203184c254fdecfa206310'
client = Client(account_sid, auth_token)
message = client.messages.create(
  from_='+19388678241',
  body='helllo i am under the water please help!!!',
  to='+12538839270'
)
print(message.sid)