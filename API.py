from SPARQLWrapper import SPARQLWrapper, JSON
from time import sleep

def execute_query(query):
    # Initialize SPARQL endpoint
    while True:
        try:
            sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
            sparql.setReturnFormat(JSON)

            sparql.setQuery(query)
            results = sparql.query().convert()
            return results
        except:
            sleep(1)
