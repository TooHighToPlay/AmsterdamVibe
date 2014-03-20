from rdflib import Namespace, BNode, Literal, URIRef
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.plugins.memory import IOMemory
import dbpedia

def createTurtle(eventid,dbpediaGenres,artists):
	ns=Namespace("http://amsterdamvibe.nl#")
	dbpediaOntologyNs=Namespace("http://dbpedia.org/ontology/")
	
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

def processDescriptionText(eventid,text,dbpediaGenres):
	dbpediaGenresFoundInText = dbpedia.extractMusicGenreNamesFromText(dbpediaGenres,text)
	dbpediaArtistsFoundInText = dbpedia.extractArtistsFromText(text)

#WORK IN PROGRESS