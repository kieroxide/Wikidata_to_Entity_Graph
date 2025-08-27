from SPARQLWrapper import SPARQLWrapper, JSON
import json


def execute_query(query):
    # Initialize SPARQL endpoint
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)

    sparql.setQuery(query)
    results = sparql.query().convert()
    return results
