__author__ = 'KevinGee'

import facebook
import json

def writeJsontoFile(o, f):
    f.write(json.dumps(o, indent=1))

# !!!
# PUT YOUR ACCESS TOKEN IN THE FILE BELOW!!!
# !!!
f = open('access_token.txt', 'r')
ACCESS_TOKEN = f.read()
f.close()

g = facebook.GraphAPI(ACCESS_TOKEN)

clubList = []

# Read club list and put it in an array
clubFile = open('clubs.txt', 'r')
for line in clubFile:
	if (line.startswith('#')):
		continue
	array = line.split(';')
	clubList.append((array[0], array[1].strip()))
clubFile.close()

# Output page info and info about events
for club in clubList:
	clubName = club[0].strip()
	clubId = club[1].strip()
	pageFile = open('pages/page_' + clubName + '.json', 'w')
	pageJson = g.get_object(clubId)
	writeJsontoFile(pageJson, pageFile)
	pageFile.close()

	# Get event list of concrete club
	eventList = g.get_connections(clubId, 'events')

	eventFile = open('events/events_' + clubName + '.json', 'w')
	counter = 0

	# Update event list with info about event under name "eventdata" : {concrete data}
	for event in eventList['data']:
		eventId = event['id']
		party = g.get_object(eventId)
		eventList['data'][counter]['eventdata'] = party
		counter+=1

	writeJsontoFile(eventList, eventFile)
	eventFile.close()











#OUTPUT to a nice file
f = open('page.json', 'w')

writeJsontoFile(g.get_object('301130305994'), f)

f.close()

f = open('melkwegEvents.json', 'w')

melkwegEvents = g.get_connections('301130305994', 'events')

writeJsontoFile(melkwegEvents, f)

f.close()

f = open('party.json', 'w')

party = g.get_object('270503946447477')

writeJsontoFile(party, f)

f.close()

############## Combine JSON's

f = open('test.json', 'w')

#print melkwegEvents['data'][0]
melkwegEvents['data'][0]['eventdata'] = party
melkwegEvents['data'][1]['eventdata'] = party
writeJsontoFile(melkwegEvents, f)

f.close()

# Get info about the event
