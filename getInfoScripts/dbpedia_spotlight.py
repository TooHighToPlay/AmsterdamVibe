import requests

text = "The Rolling Stones. Elton john and maddona Never danced like this before We don't talk about it. De oorwurmdanshit 'Stolen Dance' was afgelopen zomer eenn van de aangenamere verrassingen. Het duo uit Kassel in Duitsland bestaat uit gitarist/zanger Clemens Rehbein en dj Philipp Dausch. Samen verenigen ze het beste van twee werelden: de door reggae en folk beinvloedde liedjes van Rehbein en de ferme electrobeats van Dausch. Bij de heerlijke mix die ze daarmee maken is het onmogelijk om stil te blijven staan. In Duitsland, Oostenrijk en Zwitserland zijn ze al helemaal weg van de band, in Nederland is dat ook slechts een kwestie van tijd."

dbpedia_spotlight_url="http://spotlight.dbpedia.org/rest/annotate"

def getArtistEntities(text):
	headers = {'Accept': 'application/json'}
	get_params={
		"text":text,
		"types":"MusicalArtist,Band",
		"confidence":0.2
	}
	res=requests.get(dbpedia_spotlight_url,params=get_params,headers=headers)
	#res=requests.get(dbpedia_spotlight_url,params=get_params,headers=headers)
	spotlight_json=res.json()
	entities_uris=[]
	if spotlight_json and "Resources" in spotlight_json.keys():
		for entity in spotlight_json["Resources"]:
			entities_uris.append(entity["@URI"])
	return entities_uris

if __name__=="__main__":
	entitiesURIs = getArtistEntities(text)
	print entitiesURIs