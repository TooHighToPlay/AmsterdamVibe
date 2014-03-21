from rdflib import Namespace, BNode, Literal, URIRef, RDFS, RDF
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.plugins.memory import IOMemory
import dbpedia
import simplejson as json
import sesame

amsterdamVibeUri =  "http://amsterdamvibe.nl#"
dbpediaOntologyUri = "http://dbpedia.org/ontology/"
facebookOntologyUri = "http://facebook.com#"

ns=Namespace(amsterdamVibeUri)
dbo=Namespace(dbpediaOntologyUri)
fb=Namespace(facebookOntologyUri)

store = IOMemory()

def createTurtleForEvent(eventid,dbpediaGenres,artists):
	ns=Namespace(amsterdamVibeNs)
	dbpediaOntologyNs=Namespace(dbpediaOntologyUri)
	
	event = URIRef("http://amsterdamvibe.nl/"+eventid+"#")

	store = IOMemory()

	g=ConjunctiveGraph(store=store)
	g.bind("av",ns)
	g.bind("dbo",dbpediaOntologyNs)

	gevent = Graph(store=store,identifier=event)

	print dbpediaGenres
	for dbpediaGenre in dbpediaGenres:
		graphGenre = URIRef(dbpediaGenre)
		gevent.add((event,dbpediaOntologyNs["MusicGenre"],graphGenre))

	for dbpediaArtist in artists:
		graphArtist = URIRef(dbpediaArtist)
		gevent.add((event,ns["referenceToArtist"],graphArtist))

	print(g.serialize(format="n3"))

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

def importEventsFromFile(file_path):
	eventsToReturn=[]
	with open(file_path,"r") as f:
		allEventsJson = json.load(f)
		for eventJson in allEventsJson["data"]:
			eventsToReturn.append(eventJson)
	return eventsToReturn


def createGraphForVenues(venues):
	g=ConjunctiveGraph(store=store)
	g.bind("av",ns)
	g.bind("dbo",dbo)
	g.bind("fb",fb)
	
	for venue in venues:
		venueUriRef = URIRef("http://facebook.com/"+venue["id"]+"#")

		gvenue = Graph(store=store,identifier=venueUriRef)
		gvenue.add((venueUriRef,RDF.type,fb["venue"]))
		gvenue.add((venueUriRef,RDFS.label,Literal(venue["name"])))
		gvenue.add((venueUriRef,fb["id"],Literal(venue["id"])))
		gvenue.add((venueUriRef,fb["url"],Literal(venue["url"])))

	return g.serialize(format="n3")

def createGraphForEvents(events):
	g=ConjunctiveGraph(store=store)
	g.bind("av",ns)
	g.bind("dbo",dbo)
	g.bind("fb",fb)
	
	for event in events:
		eventUriRef = URIRef("http://facebook.com/"+event["id"]+"#")

		gevent = Graph(store=store,identifier=eventUriRef)
		gevent.add((eventUriRef,RDF.type,fb["event"]))
		gevent.add((eventUriRef,RDFS.label,Literal(event["name"])))
		gevent.add((eventUriRef,fb["id"],Literal(event["id"])))
		gevent.add((eventUriRef,fb["image_url"],Literal(event["image_url"]["source"])))
		gevent.add((eventUriRef,fb["start_time"],Literal(event["start_time"])))
		gevent.add((eventUriRef,fb["description"],Literal(event["eventdata"]["description"])))
		gevent.add((eventUriRef,fb["venue"],URIRef("http://facebook.com/"+event["eventdata"]["venue"]["id"]+"#")))
		gevent.add((eventUriRef,fb["attending_total"],Literal(event["attending_total"])))

		#TODO: add info about artists and genres

	return g.serialize(format="n3")


def processDescriptionText(eventid,text,dbpediaGenres):
	dbpediaGenresFoundInText = dbpedia.extractMusicGenreNamesFromText(dbpediaGenres,text)
	dbpediaArtistsFoundInText = dbpedia.extractArtistsFromText(text)

	createTurtle(eventId,processDescriptionText,)

if __name__=="__main__":
	venues = importVenuesFromFile("fb_data_stuff/venues.txt")
	venuesGraph = createGraphForVenues(venues)

	#TODO: loop through all files
	events = importEventsFromFile("fb_data_stuff/events/events_Melkweg.json")
	eventsGraph = createGraphForEvents(events)

	sesame.import_content("iwaf1",venuesGraph)
	sesame.import_content("iwaf1",eventsGraph)