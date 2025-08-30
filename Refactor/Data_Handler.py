from Wikidata_Client import Wikidata_Client
import os
import json

class Data_Handler:
    """Handles fetching, formatting, and saving Wikidata entity and property data."""
    def __init__(self):
        self.wiki_client = Wikidata_Client()

        self.entities = {}
        self.properties = {}
        self.relations = {}

        self.__jsonDir = "./json"
        self.__entity_path = "./json/entities.json"
        self.__property_path = "./json/properties.json"
        self.__relations_path = "./json/relations.json"
    
    def fetch_relations_data(self, entity_ids, property_ids, relations):
        """Fetch data (only labels right now) for given entities and properties, and format relations."""
        self.relations = self.__convert_relations_to_dict(relations)
        self.entities = self.wiki_client.get_entity_data(entity_ids)
        self.properties = self.wiki_client.get_property_data(property_ids)

    def save_all(self):
        """
        Save all collected data (relations, entities, properties) to JSON files.
        Uses internal paths defined in self.__entity_path, self.__property_path, and self.__relations_path.
        """
        self.__save_to_file(self.relations, self.__relations_path)
        self.__save_to_file(self.entities, self.__entity_path)
        self.__save_to_file(self.properties, self.__property_path)

    def __convert_relations_to_dict(self, relations):
        """Convert a set of (source, property, target) tuples into a nested dictionary."""

        relations_dict = {}
        for source_id, property_id, target_id in relations:
            if source_id not in relations_dict:
                relations_dict[source_id] = {}
            if property_id not in relations_dict[source_id]:
                relations_dict[source_id][property_id] = []
            relations_dict[source_id][property_id].append(target_id)
        return relations_dict

    def __save_to_file(self, obj, PATH):
        """Save a dictionary to a JSON file, creating the directory if needed."""
        if not os.path.exists(self.__jsonDir):
            os.mkdir(self.__jsonDir)
        
        with open(PATH, "w") as f:
            json.dump(dict(obj), f, indent=2)


