import urllib2
import ast

# Read client id from token.txt
f = open('token.txt', 'r')
YOUR_CLIENT_ID = f.read()
f.close()

content = urllib2.urlopen("https://graph.facebook.com/227389920779142?access_token=" + ACCESS_TOKEN + "&fields=cover").read()
content = ast.literal_eval(content)

client = soundcloud.Client(client_id=YOUR_CLIENT_ID)
track = client.get('/tracks/30709985')
print track.title