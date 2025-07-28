import smtplib
from email.message import EmailMessage


your_email = "juniorkozak6@gmail.com"
app_password = "kand szci dqes izoi"  

msg = EmailMessage()
msg.set_content("Hello! \n" \
"This is a reminder that the event you saved starts in 1 hour \n"\
"Here is the address:  \n" \
"Thank you  \n" \
"Nom Nom Me Communication Team ")
msg['Subject'] = 'Reminder from Nom Nom Near me about Event xyz'
msg['From'] = your_email
msg['To'] = 'juniorgme000@gmail.com'  # will need to be replaced with the user email 

# Send the email
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(your_email, app_password)
    smtp.send_message(msg)

print("Email sent successfully!")
