import sparql

amsterdamVibeUri =  "http://amsterdamvibe.nl/"
dbpediaOntologyUri = "http://dbpedia.org/ontology/"
facebookOntologyUri = "http://facebook.com/"
soundcloudOntologyUri = "http://soundcloud.com/tracks/"

repository_name = "iwaf1"

sesame_url = "http://127.0.0.1:8080/openrdf-workbench/repositories/"

prefixes = """
PREFIX :<http://api.foursquare.com/v2/venues/>
PREFIX dc:<http://purl.org/dc/terms/>
PREFIX onto:<http://www.ontotext.com/>
PREFIX sc:<http://soundcloud.com/tracks/>
PREFIX xml:<http://www.w3.org/XML/1998/namespace>
PREFIX av:<http://amsterdamvibe.nl#>
PREFIX fb:<http://facebook.com#>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns1:<http://dbpedia.org/ontology/>
PREFIX dbo:<http://dbpedia.org/ontology/>
PREFIX fs:<http://api.foursquare.com/v2/venues/>
PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
PREFIX owl:<http://www.w3.org/2002/07/owl#>
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
"""

def getRdfUri(uri):
	return "<"+uri+">"

def getQueryResults(repo_name,query):
	s=sparql.Service(sesame_url+repo_name+"/query")
	result = s.query(query)
	data = [] 
	for row in result:
		values = sparql.unpack_row(row)
		d = {}
		for i, v in enumerate(values):
			d[result.variables[i]] = v
		data.append(d)
	return data

def getUserSuggestedEvents(repo_name,user_id):
	print "to complete query here"

def getFutureEvents(repo_name):
	
	query = prefixes+"""
	SELECT DISTINCT ?event WHERE{
	BIND (now() AS ?crt_date)
	?event fb:start_time ?date.
	?event a fb:Event.
	FILTER(xsd:dateTime(?date) >= xsd:dateTime(?crt_date))
	}
	"""

	allFutureEvents = []
	repositoryEvents = getQueryResults(repo_name,query)
	if repositoryEvents:
		for repositoryEvent in repositoryEvents:
			eventUri=repositoryEvent["event"]
			event = getEventInfo(repo_name,eventUri)
			if repositoryEvent!=None:
				allFutureEvents.append(event)
		print allFutureEvents
		return allFutureEvents
	return None

def getEventInfo(repo_name,event_uri):
	rdfUri =getRdfUri(event_uri)
	event={}
	queryName=prefixes+"""
	SELECT DISTINCT ?label WHERE{
	%s rdfs:label ?label
	}
	"""%rdfUri
	eventNames=getQueryResults(repo_name,queryName)
	if(eventNames):
		event["name"]=eventNames[0]["label"]
	else:
		return None

	queryPosition=prefixes+"""
	SELECT DISTINCT ?latitude ?longitude WHERE{
	%s av:latitude ?latitude.
	%s av:longitude ?longitude.
	}
	"""%(rdfUri,rdfUri)
	eventPosition=getQueryResults(repo_name,queryPosition)
	if(eventPosition):
		event["latitude"]=eventPosition[0]["latitude"]
		event["longitude"]=eventPosition[0]["longitude"]

	queryAttendingTotal=prefixes+"""
	SELECT DISTINCT ?attending_total WHERE{
	%s fb:attending_total ?attending_total
	}
	"""%rdfUri
	eventAttendingTotal=getQueryResults(repo_name,queryAttendingTotal)
	if(eventAttendingTotal):
		event["attending_total"]=eventAttendingTotal[0]["attending_total"]

	queryDescription=prefixes+"""
	SELECT DISTINCT ?description WHERE{
	%s fb:description ?description
	}
	"""%rdfUri
	eventDescription=getQueryResults(repo_name,queryDescription)
	if(eventDescription):
		event["description"]=eventDescription[0]["description"]


	queryGenres=prefixes+"""
	SELECT DISTINCT ?genre_name WHERE{
	%s av:MusicGenre ?genre.
	?genre rdfs:label ?genre_name.
	}
	"""%rdfUri
	eventGenres=getQueryResults(repo_name,queryGenres)
	if(eventGenres):
		event["genres"]=[]
		for eventGenre in eventGenres:
			event["genres"].append(eventGenre["genre_name"])

	queryArtists=prefixes+"""
	SELECT DISTINCT ?artist WHERE{
	%s av:related_artist ?artist
	}
	"""%rdfUri
	eventArtists=getQueryResults(repo_name,queryArtists)
	if(eventArtists):
		event["artists"]=[]
		for eventArtist in eventArtists:
			artist=getArtistInfo(repo_name,eventArtists["artist"])
			if artist!=None:
				event["genres"].append(eventGenre["genre_name"])
	return event

def getArtistInfo(repo_name,artist_uri):
	rdfUri =getRdfUri(artist_uri)
	artist={}
	queryName=prefixes+"""
	SELECT DISTINCT ?label WHERE{
	%s rdfs:label ?label
	}
	"""%rdfUri
	artistNames=getQueryResults(repo_name,queryName)
	if(eventNames):
		event["name"]=eventNames[0]["label"]
	else:
		return None

	queryComment=prefixes+"""
	SELECT DISTINCT ?comment WHERE{
	%s rdfs:comment ?comment
	}
	"""%rdfUri
	artistComment=getQueryResults(repo_name,queryComment)
	if(artistComment):
		artist["comment"]=artistComment[0]["artistComment"]

	queryThumbnail=prefixes+"""
	SELECT DISTINCT ?thumbnail WHERE{
	%s dbo:thumbnail ?thumbnail
	}
	"""%rdfUri
	artistThumbnail=getQueryResults(repo_name,queryThumbnail)
	if(artistThumbnail):
		artist["thumbnail"]=artistThumbnail[0]["thumbnail"]

	queryTracks=prefixes+"""
	SELECT DISTINCT ?track WHERE{
	%s av:hasTrack ?track
	}
	"""%rdfUri
	artistTracks=getQueryResults(repo_name,queryTracks)
	if(artistTracks):
		artist["soundcloud_track_ids"]=[]
		for track in artistTracks:
			trackUriRef = getRdfUri(track["track"])
			queryTrackId=prefixes+"""
			SELECT DISTINCT ?track_id WHERE{
			%s av:id ?track_id
			}
			"""%trackUriRef
			artistTrackId=getQueryResults(queryTrackId)
			if(artistTrackId):
				artist["soundcloud_track_ids"].append(artistTrackId["track_id"])

	return artist

if __name__=="__main__":
	getFutureEvents(repository_name)