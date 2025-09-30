from .CleanerUtility import remove_unconnected_vertices, filter_invalid_relations

class Cleaner:
    @staticmethod
    def clean_data(source_id: str, entities: dict, properties: dict, relations: dict, console=False):
        """Combs through data culling any incombatible data, Currently properties are not touched
        as I have come across no errors"""
        
        # Remove entities with no labels
        no_label_entities = Cleaner.find_no_label_entities(entities, console)
        for no_label_entity in no_label_entities:
            entities.pop(no_label_entity, None)

        no_label_properties = Cleaner.find_no_label_properties(properties, console)
        for prop_id in no_label_properties:
            properties.pop(prop_id)
        
        relations = filter_invalid_relations(relations, entities, properties)
        
        unreferenced_entity_ids = Cleaner.find_unreferenced_entities(entities, relations, console)
        for unreference_entity_id in unreferenced_entity_ids:
            entities.pop(unreference_entity_id, None)

        entities = remove_unconnected_vertices(entities, relations)

        entities, relations = Cleaner.ensure_one_component(source_id ,relations, entities, )

        return entities, properties, relations
    
    @staticmethod
    def ensure_one_component(source_id, relations, entities):
        """Keeps only the connected component containing source_id."""
        if source_id not in entities:
            return {}, {}

        # Build undirected adjacency list
        from collections import deque, defaultdict

        adj = defaultdict(set)
        for src, rels in relations.items():
            for targets in rels.values():
                for tgt in targets:
                    adj[src].add(tgt)
                    adj[tgt].add(src)

        # BFS to find all reachable nodes from source_id
        visited = set()
        queue = deque([source_id])
        while queue:
            node = queue.popleft()
            if node not in visited:
                visited.add(node)
                queue.extend(adj[node] - visited)

        # Filter entities and relations to only those in the component
        filtered_entities = {eid: data for eid, data in entities.items() if eid in visited}
        filtered_relations = {}
        for src, rels in relations.items():
            if src in visited:
                filtered_rels = {}
                for prop, targets in rels.items():
                    filtered_targets = [t for t in targets if t in visited]
                    if filtered_targets:
                        filtered_rels[prop] = filtered_targets
                if filtered_rels:
                    filtered_relations[src] = filtered_rels

        return filtered_entities, filtered_relations
    
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
    
    @staticmethod
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


