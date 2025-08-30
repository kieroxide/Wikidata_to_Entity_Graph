from Wikidata_Client import Wikidata_Client

class Entity_Crawler:
    """Crawls Wikidata starting from a root entity to collect entity-to-entity relations."""
    def __init__(self):
        self.wiki_client = Wikidata_Client()
        self.entity_ids = set()
        self.property_ids = set()
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
        self.entity_ids.add(root_entity_id)

        for _ in range(0, crawl_depth + 1): # Add one for inital crawl
            relations = self.wiki_client.get_entity_relations(self.entity_ids)

            # Fake enums for clarity accessing tuple
            SOURCE = 0 
            PROPERTY = 1 
            TARGET = 2

            self.relations.update(relations)
            for relation in relations:
                self.entity_ids.add(relation[SOURCE])
                self.entity_ids.add(relation[TARGET])
                self.property_ids.add(relation[PROPERTY])

            