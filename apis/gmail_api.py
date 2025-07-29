import os.path
import pickle
import base64

from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ==== CONFIG ====
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = 'credentials.json'  # Download this from Google Cloud Console

# === AUTHENTICATE ===
def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

# === CREATE EMAIL ===
def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': encoded_message}

# === SEND EMAIL ===
def send_email(sender, to, subject, body):
    service = get_gmail_service()
    message = create_message(sender, to, subject, body)
    sent_message = service.users().messages().send(userId='me', body=message).execute()
    print(f"Email sent! ID: {sent_message['id']}")

# === TEST ===
if __name__ == '__main__':
    
    send_email(
        sender='juniorkozak6@gmail.com',
        to='hamedkd23@gmail.com',
        subject='Test Email from Gmail API in Python',
        body='Hello! This is a test email sent using Gmail API in Python.'
    )
