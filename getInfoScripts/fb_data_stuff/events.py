__author__ = 'KevinGee'

import facebook
import json
import urllib2
import ast

def writeJsontoFile(o, f):
    f.write(json.dumps(o, indent=1).encode('utf8'))

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
		# insert data about event
		eventList['data'][counter]['eventdata'] = party
		content = urllib2.urlopen("https://graph.facebook.com/" + eventId + "?access_token=" + ACCESS_TOKEN + "&fields=cover").read()
		content = ast.literal_eval(content)
		# insert data about event cover
		if 'cover' in content.keys():
  			eventList['data'][counter]['image_url'] = content['cover']
		else:
  			eventList['data'][counter]['image_url'] = None
			
		# insert data about people attending event
		attending = g.get_connections(eventId, 'attending')
		personCount = 0
		for person in attending['data']:
			personCount += 1
		eventList['data'][counter]['attending_total'] = personCount
		# Scrap nationalities from fb
		counter+=1

	writeJsontoFile(eventList, eventFile)
	eventFile.close()