def remove_unconnected_vertices(entities, relations):
        # Filters all unreferenced entities
        referenced_ids = set()
        # Collect all source ids
        referenced_ids.update(relations.keys()) 

        # Collect all target ids
        for relation in relations.values():
            for _, targets in relation.items():
                for target in targets:
                    referenced_ids.add(target)

        # Filter entities
        referenced_entities = {
            entity_id: entity_label
            for entity_id, entity_label in entities.items()
            if entity_id in referenced_ids
        }

        return referenced_entities

def filter_invalid_relations(relations, entities, properties):
    """Removes any relation that include entities/properties not """
    cleaned_relations = {}
    for source, relation in relations.items():
        if source not in entities:
            continue
        cleaned_relation = {}
        for prop_id, target_ids in relation.items():
            if prop_id not in properties.keys():
                continue
            kept_targets = [t for t in target_ids if t in entities]
            if kept_targets:
                cleaned_relation[prop_id] = kept_targets

        if cleaned_relation:
            cleaned_relations[source] = cleaned_relation

    return cleaned_relations