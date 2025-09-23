from .Wikidata_Client_Utility import (
    parseRelationsPayload,
    parseEntityPayload,
    parsePropertyPayload,
)
from SPARQLWrapper import SPARQLWrapper, JSON
from time import sleep
import json
import os

config_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "config.json"
)
from .Black_List import BLACKLISTED_ENTITY_TYPES

# Configuration constants
DEFAULT_BATCH_SIZE = 50
MAX_QUERY_ATTEMPTS = 3
RELATION_LIMIT = 100
WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
RETRY_DELAY = 1

with open(config_path) as f:
    config = json.load(f)

THUMBNAIL_SIZE = config["THUMBNAIL_SIZE"]


class Wikidata_Client:
    """Class to handles all API calls"""

    def batch_ids(self, ids, batch_size=DEFAULT_BATCH_SIZE):
        """Yield successive batches of IDs from a list/set."""
        ids = list(ids)
        for i in range(0, len(ids), batch_size):
            yield ids[i : i + batch_size]

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
        for batch in self.batch_ids(property_ids):
            values_clause = " ".join(f"wd:{pid}" for pid in batch)
            query = f"""
            SELECT ?property ?propertyLabel WHERE {{
                VALUES ?property {{ {values_clause} }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en, mul". }}
            }}
            """

            results_raw = self.__execute_query(query)
            if not results_raw:
                continue

            parsePropertyPayload(property_data, results_raw)

        return property_data

    def get_entity_data(self, entity_ids) -> dict:
        """Returns a dict of entity ids -> labels, type"""
        entities = dict()
        for batch in self.batch_ids(entity_ids):
            values_clause = " ".join(f"wd:{qid}" for qid in batch)
            query = f"""
            PREFIX schema: <http://schema.org/>
            SELECT ?entity ?entityLabel (SAMPLE(?type) AS ?mainType) (SAMPLE(?typeLabel) AS ?mainTypeLabel) (SAMPLE(?image) AS ?mainImage) (SAMPLE(?enwikiArticle) AS ?enwikiArticle)
                WHERE {{
                    VALUES ?entity {{ {values_clause} }}
                    OPTIONAL {{ 
                        ?entity wdt:P31 ?type .
                        ?type rdfs:label ?typeLabel .
                        FILTER(LANG(?typeLabel) = "en")
                    }}
                    OPTIONAL {{
                        ?entity wdt:P18 ?image .
                    }}
                    OPTIONAL {{
                        ?enwikiArticle schema:about ?entity ;
                        schema:isPartOf <https://en.wikipedia.org/> .
                    }}
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,mul". }}
                }}
            GROUP BY ?entity ?entityLabel"""

            results_raw = self.__execute_query(query)
            if not results_raw:
                continue

            results = results_raw.get("results", {}).get("bindings", {})
            parseEntityPayload(entities, results)

        return entities

    def get_entity_relations(
        self, entity_ids: list[str], relation_limit: int = RELATION_LIMIT, _filter=True
    ):
        """Returns up to {limit} triples (source QID, property PID, target QID)
        for a list of QIDs as a set"""

        relationships = set()
        for batch in self.batch_ids(entity_ids, 100):
            values_clause = " ".join([f"wd:{eid}" for eid in batch])

            query = f"""SELECT DISTINCT ?source ?property ?target ?sourceType ?targetType WHERE {{
                    VALUES ?source {{ {values_clause} }} 
                    ?source ?property ?target .
                    ?source wdt:P31 ?sourceType .
                    ?target wdt:P31 ?targetType ."""

            if _filter:
                for qid in BLACKLISTED_ENTITY_TYPES:
                    query += f"\n    FILTER NOT EXISTS {{ ?target wdt:P31 wd:{qid} }}"
                    query += f"\n    FILTER NOT EXISTS {{ ?source wdt:P31 wd:{qid} }}"
                    

            query += f"""
                    FILTER(STRSTARTS(STR(?target), "http://www.wikidata.org/entity/Q"))
                    FILTER(STRSTARTS(STR(?property), "http://www.wikidata.org/prop/direct/"))
                }} 
                LIMIT {relation_limit}
            """
            results_raw = self.__execute_query(query)

            if not results_raw:
                continue

            parseRelationsPayload(relationships, results_raw)
        return relationships
