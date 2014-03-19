__author__ = 'KevinGee'

import facebook
import json

# Get Events

# Get Pages then Get Events

# Melkweg 301130305994

def pp(o, f):
    f.write(json.dumps(o, indent=1))

# !!!
# PUT YOUR ACCESS TOKEN IN THE FILE BELOW!!!
# !!!
f = open('access_token.txt', 'r')
ACCESS_TOKEN = f.read()
f.close()

g = facebook.GraphAPI(ACCESS_TOKEN)

#OUTPUT to a nice file
f = open('page.json', 'w')

pp(g.get_object('301130305994'), f)

f.close()

f = open('melkwegEvents.json', 'w')

melkwegEvents = g.get_connections('301130305994', 'events')

pp(melkwegEvents, f)

f.close()

f = open('party.json', 'w')

party = g.get_object('270503946447477')

pp(party, f)

f.close()

# Get info about the event
