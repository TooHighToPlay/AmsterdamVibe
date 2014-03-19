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

# Get people count in the event

# Get info about the event
