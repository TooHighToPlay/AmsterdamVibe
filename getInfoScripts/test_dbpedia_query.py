from SPARQLWrapper import SPARQLWrapper, JSON

dbpediaSPARQLWrapper = SPARQLWrapper("http://dbpedia.org/sparql")

query = """
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbo: <http://dbpedia.org/ontology/>

select ?artist ?artist_name WHERE {
?artist a dbo:Band.
?artist rdfs:label ?artist_name.
FILTER (langMatches(lang(?artist_name),"EN")).
  FILTER (regex(?artist_name,"Rolling Stones","i")).
}
		"""

dbpediaSPARQLWrapper.setQuery(query)
dbpediaSPARQLWrapper.setReturnFormat(JSON)
results = dbpediaSPARQLWrapper.query().convert()

print results["results"]["bindings"]