import resend


resend.api_key = "re_TekTEqij_9yVALaDQMwJwmgyZ495D4iV2"



params = {
    "from": "Acme <onboarding@resend.dev>", 
    "to": ["juniorkozak6@gmail.com"],
    "subject": "Hello from Resend",
    "html": "<p>This is a <b>test email</b> sent using Resend API!</p>"
}


email = resend.Emails.send(params)
print(email)

