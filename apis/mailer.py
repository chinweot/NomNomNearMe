import smtplib
from email.message import EmailMessage

YOUR_EMAIL = "juniorkozak6@gmail.com"
APP_PASSWORD = "kand szci dqes izoi"

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = YOUR_EMAIL
    msg['To'] = to_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(YOUR_EMAIL, APP_PASSWORD)
        smtp.send_message(msg)
