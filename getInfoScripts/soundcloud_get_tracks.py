import soundcloud

number_of_tracks=10
my_client_id = "0b929371faa2dfa28bf9117f9d4b1d75"

def getSoundcloudClient():
	client = soundcloud.Client(client_id=my_client_id)
	return client

def getEmbedHtml(track_id):
	embed_html="""<iframe width="100%" height="100" scrolling="no" frameborder="no" src="https://w.soundcloud.com/player/?visual=true&url=https%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F"""
	embed_html=embed_html+str(track_id)
	embed_html=embed_html+"""&show_artwork=true&client_id=%s"></iframe>"""%my_client_id
	return embed_html

def getSoundCloudTracksIdsForArtist(client,artistName):
	track_ids=[]
	tracks = client.get('/tracks',q=artistName,limit=number_of_tracks)
	for track in tracks:
		track_ids.append(track.id)
	return track_ids

if __name__ == "__main__":
	client = getSoundcloudClient()
	track_ids=getSoundCloudTracksIdsForArtist(client,"The Rolling Stones")
	for track_id in track_ids:
		print(getEmbedHtml(track_id))