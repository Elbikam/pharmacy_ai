from twilio.rest import Client

def send_whatsapp_message(to, message):
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message,
        from_='whatsapp:+14155238886',  # Twilio's WhatsApp number
        to=f'whatsapp:{to}'
    )
    return message.sid