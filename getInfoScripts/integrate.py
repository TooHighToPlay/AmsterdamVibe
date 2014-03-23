from datetime import datetime
from os import listdir
from os.path import isfile, join
from rdflib import Namespace, BNode, Literal, URIRef, RDFS, RDF, XSD
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.plugins.memory import IOMemory
import dbpedia
import dbpedia_spotlight
import soundcloud_get_tracks
import simplejson as json
import sesame

amsterdamVibeUri =  "http://amsterdamvibe.nl/"
dbpediaOntologyUri = "http://dbpedia.org/ontology/"
facebookOntologyUri = "http://facebook.com/"
soundcloudOntologyUri = "http://soundcloud.com/tracks/"

ns=Namespace(amsterdamVibeUri)
dbo=Namespace(dbpediaOntologyUri)
fb=Namespace(facebookOntologyUri)
sc=Namespace(soundcloudOntologyUri)

store = IOMemory()

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
	onlyfiles = [ join(directory_path,f) for f in listdir(directory_path) if isfile(join(directory_path,f)) ]
	for file_path in onlyfiles:
		with open(file_path,"r") as f:
			allEventsJson = json.load(f)
			for eventJson in allEventsJson["data"]:
				eventsToReturn.append(eventJson)
	return eventsToReturn


def createGraphForVenues(g,venues):
	for venue in venues:
		venueUriRef = URIRef("http://facebook.com/"+venue["id"]+"#")

		gvenue = Graph(store=store,identifier=venueUriRef)
		gvenue.add((venueUriRef,RDF.type,fb["venue"]))
		gvenue.add((venueUriRef,RDFS.label,Literal(venue["name"])))
		gvenue.add((venueUriRef,fb["id"],Literal(venue["id"])))
		gvenue.add((venueUriRef,fb["url"],Literal(venue["url"])))

def createGraphForEvents(g,events):
	for event in events:
		eventUriRef = URIRef("http://facebook.com/"+event["id"]+"#")

		gevent = Graph(store=store,identifier=eventUriRef)
		gevent.add((eventUriRef,RDF.type,fb["event"]))
		gevent.add((eventUriRef,RDFS.label,Literal(event["name"])))
		gevent.add((eventUriRef,fb["id"],Literal(event["id"])))
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
				gevent.add((eventUriRef,fb["venue"],URIRef("http://facebook.com/"+event["eventdata"]["venue"]["id"]+"#")))
		gevent.add((eventUriRef,fb["attending_total"],Literal(event["attending_total"])))

def getRdfUri(uri):
	return "<"+uri+">"

def createGraphForEventArtistsAndGenres(g,events):
	count =0 
	allArtistUris = []
	for event in events:
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

		if count==5:
			break

		print "processed artists for "+str(count)+" out of "+str(len(events))+" events"
	# if count==2:
	# 	break

	#now add soundcloud tracks id data to all artists

	count = 0 
	soundcloudClient = soundcloud_get_tracks.getSoundcloudClient()
	for artistUri in allArtistUris:
		rdfArtistUri = getRdfUri(artistUri)
		extractArtistInfoAndAddToGraph(g,rdfArtistUri)
		count = count+1
		print "processed artist info for "+str(count)+" out of "+str(len(allArtistUris))+" artists"

def extractArtistInfoAndAddToGraph(g,rdfArtistUri):
	artistName = dbpedia.getArtistEnglishName(rdfArtistUri)

	if(artistName!=None):
		#attach to it dbpedia data
		artistUriRef = URIRef(artistUri)
		gartist = Graph(store=store,identifier=artistUriRef)

		gartist.add((artistUriRef,RDFS.label,Literal(artistName)))
		gartist.add((artistUriRef,RDF.type,ns["ArtistEntity"]))

		commentDbpediaData = dbpedia.getArtistComment(rdfArtistUri)
		if "comment" in commentDbpediaData[0].keys():
			gartist.add((artistUriRef,RDFS.comment,Literal(commentDbpediaData[0]["comment"]["value"])))

		thumbnailDbpediaData = dbpedia.getArtistThumbnail(rdfArtistUri)
		if "thumbnail" in thumbnailDbpediaData[0].keys():
			gartist.add((artistUriRef,dbo["thumbnail"],Literal(thumbnailDbpediaData[0]["thumbnail"]["value"])))

		genresDbpediaData = dbpedia.getArtistGenres(rdfArtistUri)
		for genre in genresDbpediaData:
			gartist.add((artistUriRef,dbo["MusicGenre"],Literal(genre["genre"]["value"])))

		#attach soundcloud data
		trackIds = soundcloud_get_tracks.getSoundCloudTracksIdsForArtist(soundcloudClient,artistName)
		if trackIds and len(trackIds)>0:
			for trackId in trackIds:
				trackUriRef = sc[str(trackId)]
				gtrack = Graph(store=store,identifier=trackUriRef)
				gtrack.add((trackUriRef,RDF.type,sc["track"]))
				gtrack.add((trackUriRef,sc["id"],Literal(str(trackId))))

				gartist.add((artistUriRef,ns["hasTrack"],trackUriRef))

def createGraphForGenres(g,genreNames,genreRelations):
	for genre in genreNames:
		genreUri = URIRef(genre["genre"]["value"])
		ggenre = Graph(store=store,identifier=genreUri)
		ggenre.add((genreUri,RDFS.label,Literal(genre["genre_name"]["value"])))
		ggenre.add((genreUri,RDF.type,dbo["MusicGenre"]))

	for genreRelation in genreRelations:
		genre1UriRef = URIRef(genreRelation["genre1"]["value"])
		genre2UriRef = URIRef(genreRelation["genre2"]["value"])
		relationUriRef = URIRef(genreRelation["relation"]["value"])
		ggenre = Graph(store=store,identifier=genre1UriRef)
		ggenre.add((genre1UriRef,relationUriRef,genre2UriRef))

if __name__=="__main__":
	venues = importVenuesFromFile("fb_data_stuff/venues.txt")
	events = importEventsFromDirectory("fb_data_stuff/events/")
	#genreRelations = dbpedia.getDBpediaGenreRelations()
	#genreNames = dbpedia.getDbpediaMusicGenres()

	g=ConjunctiveGraph(store=store)
	g.bind("av",ns)
	g.bind("sc",sc)
	g.bind("dbo",dbo)
	g.bind("fb",fb)

	#eventsGraph = createGraphForEvents(events)
	venuesGraph = createGraphForVenues(g,venues)
	artistAndGenresGraph = createGraphForEventArtistsAndGenres(g,events)

	#genreRelationsGraph = createGraphForGenres(genreNames,genreRelations)

	with open("test.ttl","w") as f:
		f.write(artistAndGenresGraph)

	#sesame.import_content("iwaf1",venuesGraph)
	#sesame.import_content("iwaf1",eventsGraph)