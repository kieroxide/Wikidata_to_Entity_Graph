from SPARQLWrapper import SPARQLWrapper, JSON
from time import sleep

class Wikidata_Client:
    """Class to handles all API calls"""
    def __init__(self):
        pass

    def __execute_query(self, query):
        """Takes a sparql query for wikidata and executes it"""
        attempts = 0
        while True:
            try:
                sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
                sparql.setReturnFormat(JSON)

                sparql.setQuery(query)
                results = sparql.query().convert()
                return results
            except Exception as e:
                attempts += 1
                if attempts >= 5:
                    print(f"Number of Attempts exceeded for {query}")
                    print(f"Error {e}")
                    return None
                sleep(1)

    def get_entity_relations(self, entity_ids: list[str], property_limit: int = 100):
        """Returns up to {limit} triples (source QID, property PID, target QID) 
        for a list of QIDs as a set"""

        relationships = set()

        values_clause = " ".join([f"wd:{eid}" for eid in entity_ids])
        query = f"""
            SELECT ?source ?property ?target WHERE {{
              VALUES ?source {{ {values_clause} }}
              ?source ?property ?target .
              FILTER(STRSTARTS(STR(?target), "http://www.wikidata.org/entity/Q"))
            }} LIMIT {property_limit}
        """

        data = self.__execute_query(query)
        if not data:
            return relationships

        for result in data["results"]["bindings"]:
            source_id = result["source"]["value"].split("/").pop()
            property_id = result["property"]["value"].split("/").pop()
            target_id = result["target"]["value"].split("/").pop()
            relationships.add((source_id, property_id, target_id))

        return relationships