from py.Wikidata_Client import Wikidata_Client
from py.Data_Handler import Data_Handler

class Entity_Crawler:
    """Crawls Wikidata starting from a root entity to collect entity-to-entity relations."""
    def __init__(self, data_handler: Data_Handler):
        self.wiki_client = Wikidata_Client()
        self.entity_ids = {id for id in data_handler.entities.keys()}
        self.property_ids = {id for id in data_handler.properties.keys()}
        self.relations = set()

    def __str__(self):
        data = {
            "entity_ids" : [entity_id for entity_id in self.entity_ids],
            "property_ids" : [property_id for property_id in self.property_ids],
            "relations" : [relation for relation in self.relations]
        }
        return str(data)

    def crawl_wiki(self, root_entity_id , crawl_depth = 0):
        """Crawls Wikidata starting from a root entity, collecting relations and expanding to 
        newly discovered entities up to a specified depth."""
        
        # If we have existing entities, start from all of them for deeper searches
        if self.entity_ids:
            print(f"Resuming crawl with {len(self.entity_ids)} existing entities")
            current_ids = self.entity_ids.copy()  # Start from ALL existing entities
        else:
            current_ids = {root_entity_id}  # Fresh start
            self.entity_ids.add(root_entity_id)

        
        for _ in range(0, crawl_depth + 1): # Add one for initial crawl
            if not current_ids: break
            
            relations = self.wiki_client.get_entity_relations(current_ids)
            self.relations.update(relations)

            # Fake enums for clarity accessing tuple
            SOURCE = 0 
            PROPERTY = 1 
            TARGET = 2

            self.entity_ids.update(current_ids)
            next_ids = set()
            for relation in relations:
                next_ids.add(relation[TARGET])
                self.property_ids.add(relation[PROPERTY])

            next_ids -= self.entity_ids
            current_ids = next_ids

            