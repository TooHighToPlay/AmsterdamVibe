from SPARQLWrapper import SPARQLWrapper, JSON
import re
import simplejson as json
import string
import rdflib
from rdflib import Namespace, BNode, Literal, URIRef
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.plugins.memory import IOMemory
from urllib import quote_plus

dbpediaSPARQLWrapper = SPARQLWrapper("http://dbpedia.org/sparql")

def is_uppercase(word):
	if word[0] in string.ascii_uppercase:
		return True
	else:
		return False

#simple entity extraction - to be replaced with opensahara
def extractNamedEntities(text):
	namedEntities=[]
	lines = text.split("\n")
	for line in lines:
		words=line.split(" ")
		i=0
		while i<len(words):
			namedEntity=[words[i]]
			if(is_uppercase(words[i])):
				inNamedEntity=True
				if(not ("." in words[i] or "," in words[i])): 
					for j in range(i+1,len(words)):
						i=j+1
						if(not is_uppercase(words[j])):
							inNamedEntity=False
							break
						else:
							namedEntity.append(words[j])
						if("." in words[j] or "," in words[j]):
							inNamedEntity=False
							break
				else: i=i+1
				#"failsafe" for all caps text
				if(len(namedEntity)>0 and len(namedEntity)<10):
					namedEntityString = " ".join(namedEntity)
					if("."==namedEntityString[-1] or ","==namedEntityString[-1]):
						namedEntityString=namedEntityString[0:-1]
					namedEntities.append(namedEntityString)
			else:
				i=i+1
	return namedEntities

def getDbpediaMusicGenres():
	dbpediaSPARQLWrapper.setQuery("""
	    PREFIX dbo: <http://dbpedia.org/ontology/>
	    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
	    SELECT DISTINCT ?genre ?genre_name
	    WHERE { 
	    ?genre a dbo:MusicGenre.
	  	?genre foaf:name ?genre_name.
	     }
	""")
	dbpediaSPARQLWrapper.setReturnFormat(JSON)
	results = dbpediaSPARQLWrapper.query().convert()

	return results["results"]["bindings"]

def dumpGenresToFile(dbpediaGenres):
	f = open("dbpediaGenres.json","w")
	json.dump(dbpediaGenres,f)
	f.close()

def loadGenres():
	f=open("dbpediaGenres.json","r")
	dbpediaGenres = json.load(f)
	return dbpediaGenres

def extractMusicGenreNamesFromText(dbpediaGenres,text):
	foundDbpediaGenres = []
	for genre in dbpediaGenres:
		genreDbpediaIdentifier = genre["genre"]["value"]
		genreName = genre["genre_name"]["value"]
		match=re.search(genreName.encode('utf-8'),text.encode('utf-8'),re.I)
		if match:
			foundDbpediaGenres.append(genreDbpediaIdentifier)
	return foundDbpediaGenres

def getArtistOrBandForEntityNames(artist):
	query = """
	    PREFIX dbo: <http://dbpedia.org/ontology/>
	    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
	    SELECT DISTINCT ?artist
	    WHERE { {
	    ?artist a dbo:MusicalArtist .
	    ?artist foaf:name ?name .
	    FILTER(regex(?name,"%s","i"))
	    } UNION {
	    ?artist a dbo:Band .
	    ?artist foaf:name ?name .
	    FILTER(regex(?name,"%s","i"))
	    }
	    }
	"""%(artist,artist)
	dbpediaSPARQLWrapper.setQuery(query)
	dbpediaSPARQLWrapper.setReturnFormat(JSON)
	results = dbpediaSPARQLWrapper.query().convert()

	return results["results"]["bindings"]

text = "Rolling Stones. Never danced like this before We don't talk about it. De oorwurmdanshit 'Stolen Dance' was afgelopen zomer eenn van de aangenamere verrassingen. Het duo uit Kassel in Duitsland bestaat uit gitarist/zanger Clemens Rehbein en dj Philipp Dausch. Samen verenigen ze het beste van twee werelden: de door reggae en folk beinvloedde liedjes van Rehbein en de ferme electrobeats van Dausch. Bij de heerlijke mix die ze daarmee maken is het onmogelijk om stil te blijven staan. In Duitsland, Oostenrijk en Zwitserland zijn ze al helemaal weg van de band, in Nederland is dat ook slechts een kwestie van tijd."

def getUnicodeConverted(text):
	return unicode(text,'raw-unicode-escape')

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
		artistDbpediaId = dbpediaArtist['artist']['value']
		print(artistDbpediaId)
		if artistDbpediaId:
			graphArtist = URIRef(artistDbpediaId)
			gevent.add((event,ns["referenceToArtist"],graphArtist))

	print(g.serialize(format="n3"))

def processDescriptionText(eventid,text,dbpediaGenres):
	dbpediaGenresFoundInText = extractMusicGenreNamesFromText(dbpediaGenres,text)
	namedEntities = extractNamedEntities(text)

	artistsInText = []
	for namedEntity in namedEntities:
		artists = getArtistOrBandForEntityNames(namedEntity)
		if(len(artists)>0):
			artistsInText.append(artists[0])

	print(createTurtle("1234",dbpediaGenresFoundInText,artistsInText))


if __name__ == "__main__":
	dbpediaGenres = loadGenres()
	processDescriptionText("1234",text,dbpediaGenres)