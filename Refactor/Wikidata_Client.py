from SPARQLWrapper import SPARQLWrapper, JSON
from time import sleep

class Wikidata_Client:
    """Class to handles all API calls"""
    def __init__(self):
        pass

    def execute_query(self, query):
        """Takes a sparql query for wikidata and executes it"""
        attempts = 0
        while True:
            try:
                sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
                sparql.setReturnFormat(JSON)

                sparql.setQuery(query)
                results = sparql.query().convert()
                return results
            except:
                attempts += 1
                if attempts >= 5:
                    print(f"Number of Attempts exceeded for {query}")
                    return None
                sleep(1)

    def get_entity_relations(self, entity_id: str, property_limit: str = 10):
        """Returns up to {limit} triples (property PID, target QID) from a source QID as a set"""
        relationships = set()

        query = f"""SELECT ?property ?target WHERE {{
                  wd:{entity_id} ?property ?target .
                  # Filters for only Entity -> Entity relationships
                    FILTER(STRSTARTS(STR(?target), "http://www.wikidata.org/entity/Q")) 
                }} LIMIT {property_limit}"""
        
        data = self.execute_query(query)
        # Returns empty set if wikidata fetch was no successful
        if not data:
            return relationships
        
        results = data["results"]["bindings"]
        for result in results:
            property_id = result["property"]["value"].split("/").pop()
            target_id = result["target"]["value"].split("/").pop()
            relationships.add((entity_id, property_id, target_id))

        return relationships