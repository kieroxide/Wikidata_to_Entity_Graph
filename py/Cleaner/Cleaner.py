from .CleanerUtility import remove_unconnected_vertices, filter_invalid_relations

class Cleaner:
    @staticmethod
    def clean_data(entities: dict, properties: dict, relations: dict, console=False):
        """Combs through data culling any incombatible data, Currently properties are not touched
        as I have come across no errors"""

        # Removes entities and properties with no labels/ bad labels
        # Removes relations that reference missing entities/properties
        # Remove entities with no relations

        no_label_entities = Cleaner.find_no_label_entities(entities, console)
        
        # Remove entities with no labels
        for no_label_entity in no_label_entities:
            entities.pop(no_label_entity, None)

        # Remove properties with no labels
        no_label_properties = Cleaner.find_no_label_properties(properties, console)
        for label in no_label_properties:
            properties.pop(label, None)
            
        entities = remove_unconnected_vertices(entities, relations)
        relations = filter_invalid_relations(relations, entities, properties)
        return entities, properties, relations
    
    @staticmethod
    def find_no_label_entities(entities, console=False):
        if not entities:
            return set()
        
        no_label_ids = set()
        
        for entity_id, entity_data in entities.items():
            entity_label = entity_data.get("label", entity_id)
            
            # Tests for unknown label entities
            if entity_id == entity_label:
                no_label_ids.add(entity_id)

        if no_label_ids:
            if console:
                print(f"Label Test Failed: {no_label_ids}")
            return no_label_ids
        elif console:
            print("Entity test passed!")

        return set()
    
    @staticmethod
    def find_no_label_properties(properties, console=False):
        if not properties:
            return set()
        
        no_label_ids = set()
        
        for prop_id, prop_label in properties.items():
            # Tests for unknown label entities
            if prop_id == prop_label:
                no_label_ids.add(prop_id)
        
        if no_label_ids:
            if console:
                print(f"Label Test Failed: {no_label_ids}")
            return no_label_ids

        if console:
            print("Entity test passed!")
        return set()
        
    def find_unreferenced_entities(entities, relations, console=False):
        all_ids = set()

        for source_id, relation in relations.items():
            all_ids.add(source_id)
            for _, target_ids in relation.items():
                for target_id in target_ids:
                     all_ids.add(target_id)

        non_mapped_ids = set()
        for id in all_ids:
            if id not in entities.keys():
                non_mapped_ids.add(id)

        if non_mapped_ids:
            if console:
                print(non_mapped_ids)
            return non_mapped_ids
        else:
            if console:
                print("All relation test passed!")
            return set()


