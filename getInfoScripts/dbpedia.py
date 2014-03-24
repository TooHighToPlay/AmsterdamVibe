from SPARQLWrapper import SPARQLWrapper, JSON
import re
import json
import string
import rdflib
import dbpedia_spotlight

#alternate link: http://dbpedia-live.openlinksw.com/sparql
#alternate link: http://dbpedia.org/sparql
dbpediaSPARQLWrapper = SPARQLWrapper("http://dbpedia-live.openlinksw.com/sparql")

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

def getJsonDBpediaResults(query):
	try:
		dbpediaSPARQLWrapper.setQuery(query)
		dbpediaSPARQLWrapper.setReturnFormat(JSON)
		results = dbpediaSPARQLWrapper.query().convert()
		return results["results"]["bindings"]
	except Exception as e:
		print e
		return None

def getRdfUri(uri):
	return "<"+uri+">"

def getDbpediaArtists():
	query = """
	    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		PREFIX dbo: <http://dbpedia.org/ontology/>
		PREFIX foaf: <http://xmlns.com/foaf/0.1/>

		SELECT DISTINCT ?artist ?artist_name WHERE {
			{
			  ?artist a dbo:MusicalArtist.
			  ?artist foaf:name ?artist_name
			} UNION {
			  ?artist a dbo:Band.
			  ?artist foaf:name ?artist_name
			}
		}
	"""
	return getJsonDBpediaResults(query)

def getDbpediaMusicGenres():
	query = """
	    PREFIX dbo: <http://dbpedia.org/ontology/>
	    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
	    SELECT DISTINCT ?genre ?genre_name
	    WHERE { 
	    ?genre a dbo:MusicGenre.
	  	?genre rdfs:label ?genre_name.
	  	FILTER langMatches(lang(?genre_name),"EN").
	    }
	"""
	return getJsonDBpediaResults(query)

def getDBpediaGenreRelations():
	query = """
	PREFIX dbo: <http://dbpedia.org/ontology/>
	SELECT ?genre1 ?relation ?genre2 WHERE 
	{
	?genre1 a dbo:MusicGenre.
	?genre2 a dbo:MusicGenre.
	?genre1 ?relation ?genre2.
	?relation rdfs:range dbo:MusicGenre.
	}
	"""
	return getJsonDBpediaResults(query)

def getAndSaveAllDbpediaData():
	print "getting genres data"
	musicGenresJson = getDbpediaMusicGenres()
	f = open("getInfoScripts/dbpediaGenres.json","w")
	json.dump(musicGenresJson,f)
	f.close()

	print "getting artists data"
	dbpediaArtistsJson = getDbpediaArtists()
	f = open("getInfoScripts/dbpediaArtists.json","w")
	json.dump(dbpediaArtistsJson,f)
	f.close()

def loadGenres():
	f=open("getInfoScripts/dbpediaGenres.json","r")
	dbpediaGenres = json.load(f)
	f.close()
	return dbpediaGenres

def loadArtists():
	f=open("getInfoScripts/dbpediaArtists.json","r")
	dbpediaArtists = json.load(f)
	f.close()
	return dbpediaArtists

def extractMusicGenreNamesFromText(text):
	foundDbpediaGenres = []
	for genre in dbpediaGenres:
		genreDbpediaIdentifier = genre["genre"]["value"]
		genreName = genre["genre_name"]["value"]
		match=re.search(re.escape(genreName.encode('utf-8')),text.encode('utf-8'),re.I)
		if match:
			foundDbpediaGenres.append(genreDbpediaIdentifier)
	return foundDbpediaGenres

def extractArtistsFromText(text):
	foundDbpediaArtists = dbpedia_spotlight.getArtistEntities(text)
	return foundDbpediaArtists

def getArtistEnglishName(artistUri):
	rdfUri = getRdfUri(artistUri)
	query = """
	    PREFIX dbo: <http://dbpedia.org/ontology/>
	    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
	    SELECT DISTINCT ?artist_name
	    WHERE { 
	    %s rdfs:label ?artist_name.
	  	FILTER(langMatches(lang(?artist_name), "EN")).
	    } LIMIT 1
	"""%rdfUri
	dbpediaResults = getJsonDBpediaResults(query)
	if dbpediaResults and len(dbpediaResults)>0:
		artistName = dbpediaResults[0]["artist_name"]["value"]
		return artistName
	return getJsonDBpediaResults(query)

def getArtistComment(artistUri):
	rdfUri = getRdfUri(artistUri)
	query = """
		PREFIX dbo: <http://dbpedia.org/ontology/>
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		select distinct ?artist ?comment WHERE {
		%s rdfs:comment ?comment.
		FILTER(langMatches(lang(?comment),"EN")).
		}
	"""%rdfUri
	return getJsonDBpediaResults(query)

def getArtistGenres(artistUri):
	rdfUri = getRdfUri(artistUri)
	query = """
		PREFIX dbo: <http://dbpedia.org/ontology/>
		select distinct ?genre WHERE {
		%s dbo:genre ?genre.
		}
	"""%rdfUri
	return getJsonDBpediaResults(query)

def getArtistThumbnail(artistUri):
	rdfUri = getRdfUri(artistUri)
	query = """
		PREFIX dbo: <http://dbpedia.org/ontology/>
		select distinct ?thumbnail WHERE {
		%s dbo:thumbnail ?thumbnail.
		}
	"""%rdfUri
	return getJsonDBpediaResults(query)

def getArtistWithNmae(artistName):
	query = """
		PREFIX dbo: <http://dbpedia.org/ontology/>
		select distinct ?artist WHERE {
		{
		?artist a dbo:MusicalArtist.
		?artist rdfs:label ?artist_name.
		FILTER regex(?artist_name,"%s","i").
		} UNION {
		?artist a dbo:Band.
		?artist rdfs:label ?artist_name.
		FILTER regex(?artist_name,"%s","i").
		}
		}
	"""%(artistName,artistName)
	return getJsonDBpediaResults(query)

def getGenreWithName(genreName):
	query = """
		PREFIX dbo: <http://dbpedia.org/ontology/>
		select distinct ?genre WHERE {
		{
		?genre a dbo:MusicGenre.
		?genre rdfs:label ?genreName.
		FILTER regex(?genreName,"%s","i").
		}
	"""%genreName
	return getJsonDBpediaResults(query)


# def getArtistOrBandForEntityNames(artist):
# 	query = """
# 	    PREFIX dbo: <http://dbpedia.org/ontology/>
# 	    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
# 	    SELECT DISTINCT ?artist ?name
# 	    WHERE { {
# 	    ?artist a dbo:MusicalArtist .
# 	    ?artist foaf:name ?name .
# 	    FILTER(regex(?name,"^%s$","i"))
# 	    } UNION {
# 	    ?artist a dbo:Band .
# 	    ?artist foaf:name ?name .
# 	    FILTER(regex(?name,"^%s$","i"))
# 	    }
# 	    }
# 	"""%(artist,artist)
# 	dbpediaSPARQLWrapper.setQuery(query)
# 	dbpediaSPARQLWrapper.setReturnFormat(JSON)
# 	results = dbpediaSPARQLWrapper.query().convert()

	return results["results"]["bindings"]




def getUnicodeConverted(text):
	return unicode(text,'raw-unicode-escape')

dbpediaGenres = loadGenres()
