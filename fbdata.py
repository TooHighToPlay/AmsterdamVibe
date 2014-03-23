import facebook
import json
import requests

def get_all_data(url):
    data = []
    response = g.get_object(url)
    data.extend(response['data'])

    while 'paging' in response and 'next' in response['paging']:
        response = requests.get(response['paging']['next']).json()
        data.extend(response['data'])

    return data

# put your own token here
TOKEN = ''

# Create a connection to the Graph API with your access token
g = facebook.GraphAPI(TOKEN)

# list of events like
#{u'id': u'1474661709416555',
#u'location': u'room EC101, Faculty of Automatic Control and Computers',
#u'name': u'Ixia Day 2014',
#u'rsvp_status': u'attending',
#u'start_time': u'2014-03-27T14:00:00+0200',
#u'timezone': u'Europe/Bucharest'}
events = get_all_data('/me/events')

# list of likes like
# {u'category': u'Travel/leisure', u'created_time': u'2014-03-23T11:23:17+0000', u'name': u'FamilyVacation.com', u'id': u'260157990676396'}
likes = get_all_data('/me/likes')

artists = [l for l in likes if l['category'] == 'Musician/band']
genres = [l for l in likes if l['category'] == 'Musical genre']

