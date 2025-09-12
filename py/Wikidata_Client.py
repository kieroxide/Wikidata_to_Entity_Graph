from SPARQLWrapper import SPARQLWrapper, JSON
from time import sleep

# Configuration constants
DEFAULT_BATCH_SIZE = 50
MAX_QUERY_ATTEMPTS = 3
RELATION_LIMIT = 100
WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
RETRY_DELAY = 1        

# AI generated list of important entity types
USEFUL_ENTITY_TYPES = {
    # People & Organizations
    "Q5",        # human
    "Q43229",    # organization
    "Q4830453",  # business
    "Q891723",   # public company
    "Q783794",   # company
    "Q327333",   # government agency
    "Q2659904",  # government organization
    "Q17149090", # political organization
    "Q7278",     # political party
    "Q163740",   # nonprofit organization

    # Places
    "Q515",      # city
    "Q486972",   # human settlement
    "Q3024240",  # historical country
    "Q7275",     # state
    "Q10864048", # first-level administrative division
    "Q1134686",  # continent
    "Q23442",    # island
    "Q8502",     # mountain
    "Q4022",     # river
    "Q23397",    # lake

    # Media & Culture
    "Q11424",    # film
    "Q5398426",  # television series
    "Q7725634",  # literary work
    "Q571",      # book
    "Q482994",   # album
    "Q7366",     # song
    "Q11446",    # ship
    "Q15416",    # television program
    "Q1107",     # anime

    # Science & Nature
    "Q16521",    # taxon
    "Q7239",     # organism
    "Q427626",   # taxonomic rank
    "Q3695082",  # chemical compound
    "Q11173",    # chemical element
    "Q523",      # star
    "Q634",      # planet
    "Q2199864",  # celestial body

    # Objects & Concepts
    "Q35120",    # entity
    "Q12136",    # disease
    "Q1190554",  # occurrence
    "Q1656682",  # event
    "Q1047113",  # specialty
    "Q11862829", # academic discipline
    "Q838948",   # work of art
    "Q571",      # book
    "Q277759",   # book series
}

class Wikidata_Client:
    """Class to handles all API calls"""
    def __init__(self):
        pass

    def batch_ids(self, ids, batch_size=DEFAULT_BATCH_SIZE):
        """Yield successive batches of IDs from a list/set."""
        ids = list(ids)  
        for i in range(0, len(ids), batch_size):
            yield ids[i:i + batch_size]
    
    def __execute_query(self, query):
        """Takes a sparql query for wikidata and executes it"""
        attempt = 0
        while True:
            try:
                sparql = SPARQLWrapper(WIKIDATA_ENDPOINT)
                sparql.setReturnFormat(JSON)

                sparql.setQuery(query)
                results = sparql.query().convert()
                return results
            except Exception as e:
                attempt += 1
                print(f"Attempt {attempt}/{MAX_QUERY_ATTEMPTS} failed: {e}")
                if attempt >= MAX_QUERY_ATTEMPTS:
                    print(f"Query failed after {MAX_QUERY_ATTEMPTS} attempts")
                    return None
                print(f"Error {e}")
                sleep(RETRY_DELAY)
                
    def get_property_data(self, property_ids) -> dict:
        """Returns a set of tuples of property ids and labels"""
        property_data = dict()
        for batch in (self.batch_ids(property_ids)):
            values_clause = " ".join(f"wd:{pid}" for pid in batch)
            query = f"""
            SELECT ?property ?propertyLabel WHERE {{
                VALUES ?property {{ {values_clause} }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en, mul". }}
            }}
            """

            results_raw = self.__execute_query(query)
            results = results_raw["results"]["bindings"]
            for result in results:
                pid = result["property"]["value"].split("/")[-1]
                label: str = result.get("propertyLabel", {}).get("value", pid)
                property_data[pid] = label.title()

        return property_data
    
    def get_entity_data(self, entity_ids, raw=False) -> dict:
        """Returns a dict of entity ids -> labels, type"""
        entity_data = dict()
        for batch in (self.batch_ids(entity_ids)):
            values_clause = " ".join(f"wd:{qid}" for qid in batch)
            query = f"""
            SELECT ?entity ?entityLabel (SAMPLE(?type) AS ?mainType) (SAMPLE(?typeLabel) AS ?mainTypeLabel)
            WHERE {{
                VALUES ?entity {{ {values_clause} }}
                OPTIONAL {{ 
                    ?entity wdt:P31 ?type .
                    ?type rdfs:label ?typeLabel .
                    FILTER(LANG(?typeLabel) = "en")
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,mul". }}
            }}
            GROUP BY ?entity ?entityLabel
            """
            results_raw = self.__execute_query(query)
            if raw:
                return results_raw
            
            results = results_raw["results"]["bindings"]
            for result in results:
                # Entity id and label gets
                e_id = result["entity"]["value"].split("/")[-1]

                label: str = result.get("entityLabel", {}).get("value", e_id)
                if "xml:lang" in label:
                    label = label["value"]
                # Entity Type data
                entityType: str = result.get("mainTypeLabel", {}).get("value", "Unknown")
                entity_data[e_id] =  {"label": label.title(), "type": entityType.title()}

        return entity_data
            
    def get_entity_relations(self, entity_ids: list[str], relation_limit: int = RELATION_LIMIT, _filter=True):
        """Returns up to {limit} triples (source QID, property PID, target QID) 
        for a list of QIDs as a set"""
        relationships = set()
        useful_types_str = " ".join([f"wd:{qid}" for qid in USEFUL_ENTITY_TYPES])
        for batch in self.batch_ids(entity_ids, 100):
            values_clause = " ".join([f"wd:{eid}" for eid in batch])
            query = f"""SELECT DISTINCT ?source ?property ?target WHERE {{
                    VALUES ?source {{ {values_clause} }}"""
            if _filter:
                query += "\n" + f"VALUES ?targetType {{ { useful_types_str } }}"
            query += f"""?source ?property ?target .
                    ?target wdt:P31 ?targetType .
                    FILTER(STRSTARTS(STR(?target), "http://www.wikidata.org/entity/Q"))
                    FILTER(STRSTARTS(STR(?property), "http://www.wikidata.org/prop/direct/"))
                }} 
                LIMIT {relation_limit}
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