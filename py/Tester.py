from py.Data_Handler import Data_Handler

class Tester:
    def clean_data(self, dh: Data_Handler):
        no_label_entities = self.test_entity_labels(dh)
        
        for no_label_entity in no_label_entities:
            dh.entities.pop(no_label_entity, None)

        non_mapped_ids = self.test_relations(dh)

        relations = dh.relations
        cleaned_relations = {}
        for source, relation in relations.items():
            if source in non_mapped_ids:
                continue

            cleaned_relation = {}
            for prop_id, target_ids in relation.items():
                kept_targets = [t for t in target_ids if t not in non_mapped_ids]
                if kept_targets:
                    cleaned_relation[prop_id] = kept_targets

            if cleaned_relation:
                cleaned_relations[source] = cleaned_relation
        
        dh.relations = cleaned_relations
        dh.save_all()
        
        

    def test_entity_labels(self, data_handler: Data_Handler, console=False):
        entities = data_handler.entities
        if not entities:
            return set()
        
        no_label_ids = set()
        incorrect_format_entities = set()
        
        for entity_id, entity_data in entities.items():
            entity_label = entity_data.get("label", entity_id)
            entity_type = entity_data.get("type", "Unknown")
            
            # Tests for unknown label entities
            if entity_id == entity_label:
                no_label_ids.add(entity_id)

            # Tests for incorrect format of data
            if not isinstance(entity_label, str) or entity_label != entity_label.title():
                incorrect_format_entities.add(entity_id)
        
        if no_label_ids:
            if console:
                print(f"Label Test Failed: {no_label_ids}")
            return no_label_ids

        if incorrect_format_entities:
            if console:
                print(f"Incorrect formatting on labels: {incorrect_format_entities}")
            return incorrect_format_entities

        if console:
            print("Entity test passed!")
        return set()

    def test_relations(self, data_handler: Data_Handler, console=False):
        relations = data_handler.relations
        entities = data_handler.entities

        all_ids = set()
        for source_id, relation in relations.items():
            all_ids.add(source_id)
            for prop_id, target_ids in relation.items():
                for target_id in target_ids:
                     all_ids.add(target_id)

        non_mapped_ids = set()
        for id in all_ids:
            if id not in entities:
                non_mapped_ids.add(id)

        if non_mapped_ids:
            if console:
                print(non_mapped_ids)
            return non_mapped_ids
        else:
            if console:
                print("All relation test passed!")
            return set()


