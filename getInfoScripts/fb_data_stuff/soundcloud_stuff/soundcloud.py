import soundcloud

# Read client id from token.txt
f = open('token.txt', 'r')
YOUR_CLIENT_ID = f.read()
f.close()

client = soundcloud.Client(client_id=YOUR_CLIENT_ID)
track = client.get('/tracks/30709985')
print track.title