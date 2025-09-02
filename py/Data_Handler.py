from py.Wikidata_Client import Wikidata_Client
import json
from pathlib import Path

class Data_Handler:
    """Handles fetching, formatting, and saving Wikidata entity and property data."""
    def __init__(self):
        self.wiki_client = Wikidata_Client()

        self.entities = {}
        self.properties = {}
        self.relations = {}

        self.project_root = Path(__file__).parent.parent
        self.__jsonDir = self.project_root / "json"
        self.entity_path = self.__jsonDir / "entities.json"
        self.property_path = self.__jsonDir / "properties.json"
        self.relations_path = self.__jsonDir / "relations.json"

        self.entities = self.read_file(self.entity_path)
        self.properties = self.read_file(self.property_path)
        self.relations = self.read_file(self.relations_path)
    
    def change_json_dir(self, dir_path):
        self.__jsonDir = self.project_root / dir_path
    
    def fetch_relations_data(self, entity_ids, property_ids, relations):
        """Fetch data for given entities and properties, and format relations."""
        # Filter out already known IDs
        new_entity_ids = entity_ids - {id for id in self.entities.keys()}
        new_property_ids = property_ids - {id for id in self.properties.keys()}

        # Get new data and MERGE with existing data
        new_entities = self.wiki_client.get_entity_data(new_entity_ids)
        new_properties = self.wiki_client.get_property_data(new_property_ids)

        # Merge with existing data instead of overwriting
        self.entities.update(new_entities)
        self.properties.update(new_properties)

        # Convert and merge relations
        new_relations = self.__convert_relations_to_dict(relations)
        self.relations.update(new_relations)
        
    def save_all(self, json_dir=""):
        """
        Save all collected data (relations, entities, properties) to JSON files.
        Uses internal paths defined in self.__entity_path, self.__property_path, and self.__relations_path.
        """
        if self.relations:
            self.__save_to_file(self.relations, self.relations_path, json_dir)
        if self.entities:
            self.__save_to_file(self.entities, self.entity_path, json_dir)
        if self.properties:
            self.__save_to_file(self.properties, self.property_path, json_dir)

    def __save_to_file(self, obj, PATH, json_dir, mode="w"):
        """Save a dictionary to a JSON file, creating the directory if needed."""
        self.__jsonDir.mkdir(exist_ok=True)
        
        with open(PATH, mode) as f:
            json.dump(dict(obj), f, indent=2)

    def read_file(self, PATH):
        """Save a dictionary to a JSON file, creating the directory if needed."""
        self.__jsonDir.mkdir(exist_ok=True)
        
        if not Path(PATH).exists():
            return {}
        
        with open(PATH, "r") as f:
            data = json.load(f)
        return data

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



