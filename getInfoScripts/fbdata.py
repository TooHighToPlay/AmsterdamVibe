import facebook
import json
import requests
from pprint import pprint

def get_all_data(g,url):
    data = []
    response = g.get_object(url)

    data.extend(response['data'])

    while 'paging' in response and 'next' in response['paging']:
        response = requests.get(response['paging']['next']).json()
        data.extend(response['data'])

    return data


def get_fbuser_data(fbtoken):
	# Create a connection to the Graph API with your access token
	g = facebook.GraphAPI(fbtoken)

	userevents = get_all_data(g,'/me/events')

	likes = get_all_data(g,'/me/likes')

	artists = [l for l in likes if l['category'] == 'Musician/band']
	genres = [l for l in likes if l['category'] == 'Musical genre']

	allEventsInfo = []
	for event in userevents:
		event_id = event["id"]
		event_info = g.get_object("/"+str(event_id))
		if event_info:
			allEventsInfo.append(event_info)

	return [genres,artists,allEventsInfo]

if __name__=="__main__":
	fbuser_TOKEN = 'CAACEdEose0cBAMFV2XY6GvVeZCQxm8GImv5lEqZCEeEY3Y3QGrvXuoZCzQ4jgLeBXcPPvlZCACZABf60BOJi3WhxhGiywxiLqlspA2Uet7ags2NKy8g9oAdpzsrwFbLurAUkGp6trYgPLTeBb6ixWgNsGRKiMR85r95Xk2DMBtTiKZAWyfLO7WTuQrbZBUuqwoZD'
	get_fbuser_data(fbuser_TOKEN)