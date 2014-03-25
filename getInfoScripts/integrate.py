from datetime import datetime
from os import listdir
from os.path import isfile, join
from rdflib import Namespace, BNode, Literal, URIRef, RDFS, RDF, XSD
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.plugins.memory import IOMemory
import dbpedia
import dbpedia_spotlight
import soundcloud_get_tracks
import fbdata
import json
import sesame
import sesame_repository

amsterdamVibeUri =  "http://amsterdamvibe.nl#"
dbpediaOntologyUri = "http://dbpedia.org/ontology#"
facebookOntologyUri = "http://facebook.com#"
soundcloudOntologyUri = "http://soundcloud.com#"

ns=Namespace(amsterdamVibeUri)
dbo=Namespace(dbpediaOntologyUri)
fb=Namespace(facebookOntologyUri)
sc=Namespace(soundcloudOntologyUri)

def importVenuesFromFile(file_path):
	f=open(file_path,"r")
	venues=[]
	for line in f:
		if(len(line.strip())>0):
			splitline = line.split(";")
			venue={}
			venue["name"]=splitline[0].strip()
			venue["id"]=splitline[1].strip()
			venue["url"]=splitline[2].strip()
			venues.append(venue)
	return venues

def importEventsFromDirectory(directory_path):
	eventsToReturn=[]
	onlyfiles = [ join(directory_path,f) for f in listdir(directory_path) if (isfile(join(directory_path,f)) and "events" in f) ]
	for file_path in onlyfiles:
		with open(file_path,"r") as f:
			allEventsJson = json.load(f)
			for eventJson in allEventsJson["data"]:
				eventsToReturn.append(eventJson)
	return eventsToReturn


def createGraphForVenues(store,venues):
	for venue in venues:
		venueUriRef = URIRef("http://facebook.com/"+venue["id"])

		gvenue = Graph(store=store,identifier=venueUriRef)
		gvenue.add((venueUriRef,RDF.type,fb["Venue"]))
		gvenue.add((venueUriRef,RDFS.label,Literal(venue["name"])))
		gvenue.add((venueUriRef,fb["id"],Literal(venue["id"])))
		gvenue.add((venueUriRef,fb["url"],Literal(venue["url"])))

def createGraphForEvents(store,repo_name,events,gfacebook_user=None,gfacebook_user_uriref=None):
	for event in events:
		eventUriRef = URIRef("http://facebook.com/"+event["id"])

		gevent = Graph(store=store,identifier=eventUriRef)
		gevent.add((eventUriRef,RDF.type,fb["Event"]))
		gevent.add((eventUriRef,RDFS.label,Literal(event["name"])))
		gevent.add((eventUriRef,fb["id"],Literal(event["id"])))

		if "attending_total" in event.keys():
			gevent.add((eventUriRef,fb["attending_total"],Literal(event["attending_total"])))

		if(gfacebook_user!=None and gfacebook_user_uriref!=None):
			gfacebook_user.add((gfacebook_user_uriref,ns["was_at"],eventUriRef))

		#add the rest of information
		eventAlreadyExists = sesame_repository.doesEventWithIdExist(repo_name,event["id"])
		if not eventAlreadyExists:
			if "image_url" in event.keys() and event["image_url"]!=None:
				gevent.add((eventUriRef,fb["image_url"],Literal(event["image_url"]["source"])))

			start_time_string = event["start_time"]
			start_time_string_without_timezone = start_time_string.split("+")[0]

			date_added=False
			#try to add date
			try:
				start_time_date = datetime.strptime(start_time_string_without_timezone,'%Y-%m-%dT%H:%M:%S')
				gevent.add((eventUriRef,fb["start_time"],Literal(start_time_string_without_timezone,datatype=XSD.dateTime)))
				date_added=True
			except:
				print "could not process datetime, try date instead"

			if not date_added:
				try:
					start_time_date = datetime.strptime(start_time_string_without_timezone,'%Y-%m-%d')
					gevent.add((eventUriRef,fb["start_time"],Literal(start_time_string_without_timezone,datatype=XSD.date)))
				except:
					print "could not even add event date, something wrong"

			gevent.add((eventUriRef,fb["location"],Literal(event["location"])))
			
			if "eventdata" in event.keys():
				if("description" in event["eventdata"].keys()):
					gevent.add((eventUriRef,fb["description"],Literal(event["eventdata"]["description"])))
				if("venue" in event["eventdata"].keys() and "id" in event["eventdata"]["venue"].keys()):
					gevent.add((eventUriRef,fb["at_venue"],URIRef("http://facebook.com/"+event["eventdata"]["venue"]["id"])))
					if "latitude" in event["eventdata"]["venue"].keys() and "longitude" in event["eventdata"]["venue"].keys():
						gevent.add((eventUriRef,ns["latitude"],Literal(event["eventdata"]["venue"]["latitude"])))
						gevent.add((eventUriRef,ns["longitude"],Literal(event["eventdata"]["venue"]["longitude"])))

def createGraphForEventArtistsAndGenres(store,repo_name,events):
	count =0 
	allArtistUris = []
	for event in events:
		eventAlreadyExists = sesame_repository.doesEventWithIdExist(repo_name,event["id"])
		if not eventAlreadyExists:
			eventUriRef = URIRef("http://facebook.com/"+event["id"])

			gevent = Graph(store=store,identifier=eventUriRef)
			
			if "eventdata" in event.keys():
				if("description" in event["eventdata"].keys()):
					description = event["eventdata"]["description"]
					genres = dbpedia.extractMusicGenreNamesFromText(description)
					for dbpediaGenreUri in genres:
						gevent.add((eventUriRef,ns["genre"],URIRef(dbpediaGenreUri)))
					artists = dbpedia_spotlight.getArtistEntities(description)
					for artistUri in artists:
						gevent.add((eventUriRef,ns["relatedArtist"],URIRef(artistUri)))
						if artistUri not in allArtistUris:
							allArtistUris.append(artistUri)
		
		count = count+1

		# if count==15:
		# 	break

		print "processed artists for "+str(count)+" out of "+str(len(events))+" events"
	# if count==2:
	# 	break

	#now add soundcloud tracks id data to all artists

	count = 0 
	soundcloudClient = soundcloud_get_tracks.getSoundcloudClient()
	for artistUri in allArtistUris:
		extractArtistInfoAndAddToGraph(store,artistUri,soundcloudClient)
		count = count+1
		print "processed artist info for "+str(count)+" out of "+str(len(allArtistUris))+" artists"

def extractArtistInfoAndAddToGraph(store,artistUri,soundcloudClient):
	artistName = dbpedia.getArtistEnglishName(artistUri)

	if(artistName!=None):
		#attach to it dbpedia data
		artistUriRef = URIRef(artistUri)
		gartist = Graph(store=store,identifier=artistUriRef)

		gartist.add((artistUriRef,RDFS.label,Literal(artistName)))
		gartist.add((artistUriRef,RDF.type,ns["ArtistEntity"]))

		commentDbpediaData = dbpedia.getArtistComment(artistUri)
		if commentDbpediaData and "comment" in commentDbpediaData[0].keys():
			gartist.add((artistUriRef,RDFS.comment,Literal(commentDbpediaData[0]["comment"]["value"])))

		thumbnailDbpediaData = dbpedia.getArtistThumbnail(artistUri)
		if thumbnailDbpediaData and "thumbnail" in thumbnailDbpediaData[0].keys():
			gartist.add((artistUriRef,dbo["thumbnail"],Literal(thumbnailDbpediaData[0]["thumbnail"]["value"])))

		genresDbpediaData = dbpedia.getArtistGenres(artistUri)
		for genre in genresDbpediaData:
			gartist.add((artistUriRef,dbo["MusicGenre"],URIRef(genre["genre"]["value"])))

		#attach soundcloud data
		trackIds = soundcloud_get_tracks.getSoundCloudTracksIdsForArtist(soundcloudClient,artistName)
		if trackIds and len(trackIds)>0:
			for trackId in trackIds:
				trackUriRef = URIRef("http://soundcloud.com/"+str(trackId))
				gtrack = Graph(store=store,identifier=trackUriRef)
				gtrack.add((trackUriRef,RDF.type,ns["Track"]))
				gtrack.add((trackUriRef,ns["id"],Literal(str(trackId))))

				gartist.add((artistUriRef,ns["hasTrack"],trackUriRef))

def createGraphForGenres(store,genreNames,genreRelations):
	for genre in genreNames:
		genreUri = URIRef(genre["genre"]["value"])
		ggenre = Graph(store=store,identifier=genreUri)
		ggenre.add((genreUri,RDFS.label,Literal(genre["genre_name"]["value"])))
		ggenre.add((genreUri,RDF.type,ns["MusicGenre"]))

	for genreRelation in genreRelations:
		genre1UriRef = URIRef(genreRelation["genre1"]["value"])
		genre2UriRef = URIRef(genreRelation["genre2"]["value"])
		relationUriRef = URIRef(genreRelation["relation"]["value"])
		ggenre = Graph(store=store,identifier=genre1UriRef)
		ggenre.add((genre1UriRef,relationUriRef,genre2UriRef))

def createGraphForFBUser(store,userId,userToken):
	[genres,artists,userEventsInfo] = fbdata.get_fbuser_data(userToken)

	userUri = URIRef(facebookOntologyUri+str(userId))
	gfacebook_user = Graph(store=store,identifier=userUri)
	gfacebook_user.add((userUri,RDF.type,ns["User"]))
	gfacebook_user.add((userUri,ns["fbid"],Literal(userId)))

	soundcloud_client = soundcloud_get_tracks.getSoundcloudClient()
	for artist in artists:
		artistName = artist["name"]
		dbpediaArtistsWithName = dbpedia.getArtistWithNmae(artistName)
		if(dbpediaArtistsWithName):
			artistUri = dbpediaArtistsWithName[0]["artist"]["value"]
			artistURIRef = URIRef(artistUri)
			extractArtistInfoAndAddToGraph(store,artistUri,soundcloud_client)

			gfacebook_user.add((userUri,ns["likesArtist"],artistURIRef))

	for genre in genres:
		genreName = genre["name"]
		dbpediaGenresWithName = dbpedia.getGenreWithName(genre)
		if(dbpediaGenresWithName):
			genreUri = dbpediaArtistsWithName[0]["genre"]["value"]
			genreURIRef = URIRef(genreUri)

			gfacebook_user.add((userUri,ns["likesGenre"],genreURIRef))

	createGraphForEvents(store,repo_name,userEventsInfo,gfacebook_user,userUri)
	createGraphForEventArtistsAndGenres(store,repo_name,userEventsInfo)

def gatherAndExportGenreData(repo_name):
	store = IOMemory()

	g=ConjunctiveGraph(store=store)
	g.bind("av",ns)
	g.bind("sc",sc)
	g.bind("dbo",dbo)
	g.bind("fb",fb)

	genreRelations = dbpedia.getDBpediaGenreRelations()
	genreNames = dbpedia.getDbpediaMusicGenres()
	createGraphForGenres(store,genreNames,genreRelations)


	graphString = g.serialize(format="n3")

	with open("genres.ttl","w") as f:
		f.write(graphString)

	response = sesame.import_content(repo_name,graphString)

def gatherAndExportGlobalData(repo_name):
	store = IOMemory()

	g=ConjunctiveGraph(store=store)
	g.bind("av",ns)
	g.bind("sc",sc)
	g.bind("dbo",dbo)
	g.bind("fb",fb)

	venues = importVenuesFromFile("fb_data_stuff/venues.txt")
	events = importEventsFromDirectory("fb_data_stuff/events/")
	

	createGraphForEvents(store,repo_name,events)
	createGraphForVenues(store,venues)
	createGraphForEventArtistsAndGenres(store,repo_name,events)

	graphString = g.serialize(format="n3")

	with open("global.ttl","w") as f:
		f.write(graphString)

	#response = sesame.import_content(repo_name,graphString)

def gatherAndExportUserData(repo_name,userId,userToken):
	store = IOMemory()

	g=ConjunctiveGraph(store=store)
	g.bind("av",ns)
	g.bind("sc",sc)
	g.bind("dbo",dbo)
	g.bind("fb",fb)

	createGraphForFBUser(store,userId,userToken)

	graphString = g.serialize(format="n3")
	with open("user.ttl","w") as f:
		f.write(graphString)

	response = sesame.import_content(repo_name,graphString)

if __name__=="__main__":
	repo_name="iwaf1"

	#gatherAndExportGenreData(repo_name)
	#gatherAndExportGlobalData(repo_name)

	fbuser_TOKEN = 'CAACEdEose0cBAIjGwoBZB4OsX1p83DJrL05gK89yuWr4PCDA6uO9dA60AzhDoV7ANF5cz1XCTZAGxPVC8U780vA5ygJZAPzzzqYf5EbqLOtpr4fVY3M1dLh1VfC2l7GbgXGdN2icTk9fXFZBU2UVvyJaKNZB4ucyOWMABDgRPw0OMIVeJTnNCNv9JaSh5sM3J8k7B8ZCTt8AZDZD'
	userId = "12312341234"
	gatherAndExportUserData(repo_name,userId,fbuser_TOKEN)
