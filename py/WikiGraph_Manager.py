from py.Entity_Crawler import Entity_Crawler
from py.Data_Handler import Data_Handler
from py.Tester import Tester

class WikiGraph_Manager:
    """ Manages the process of building a Wikidata entity graph. """

    def __init__(self):
        self.data_handler = Data_Handler()
        self.entity_crawler = Entity_Crawler(self.data_handler)
        self.tester = Tester()

    def build(self, source_id, depth=1, raw=False):
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
    
    def test_clean_results(self):
        self.tester.clean_data(self.data_handler)

    def test_results(self, console=False):
        self.tester.test_entity_labels(self.data_handler, console)
        self.tester.test_relations(self.data_handler, console)
