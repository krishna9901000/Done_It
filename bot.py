from twilio.rest import Client

account_sid = 'AC2bcad60c900685706eb4c4b7bca57ad4'
auth_token = 'a61e28989401f5ab0229822b39784579'
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='whatsapp:+14155238886',
  content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
  content_variables='{"1":"12/1","2":"3pm"}',
  to='whatsapp:+916238251715'
)

print(message.sid)




print(f'Message sent! SID: {message.sid}')
