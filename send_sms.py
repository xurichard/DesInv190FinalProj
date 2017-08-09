from twilio.rest import Client

# Find these values at https://twilio.com/user/account
account_sid = "ACee7629d3b852047940e7667b3df719a9"
auth_token = "0b8a98fc45556026f66922e11f5484f0"
client = Client(account_sid, auth_token)

message = client.api.account.messages.create(to="+14256236872",
                                             from_="+14142400316",
                                             body="Remember to take your medicine!")