from Wikidata_Client import Wikidata_Client
from Entity_Crawler import Entity_Crawler
from Data_Handler import Data_Handler

class WikiGraph_Manager:
    """ Manages the process of building a Wikidata entity graph. """

    def __init__(self):
        self.entity_crawler = Entity_Crawler()
        self.data_handler = Data_Handler()

    def build(self, source_id, depth=1):
        """ Crawls Wikidata starting from `source_id` up to `depth` levels
            and collects entity, property, and relation data."""
        self.entity_crawler.crawl_wiki(source_id, crawl_depth=depth)
        
        self.data_handler.fetch_relations_data(
            self.entity_crawler.entity_ids, 
            self.entity_crawler.property_ids, 
            self.entity_crawler.relations)
    
    def save_all(self):
        """ Saves all gathered data to json files"""
        self.data_handler.save_all()
