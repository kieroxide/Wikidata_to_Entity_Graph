from collections import defaultdict
from paths import Q_CODE_PATH, P_CODE_PATH, DATA_PATH
from cache import is_pcode, is_qcode, lookup_label
import json


def build_graph(data, source_qid):
    data = data["results"]["bindings"]
    QIDS = set()
    nodes = {}
    edges = defaultdict(list)

    for part in data:
        ### Nodes
        value_part = part["value"]

        # Skips any literals (non-entities) and media files
        if value_part["value"].startswith(
            "http://commons.wikimedia.org/wiki/Special:FilePath/"
        ):
            continue

        if value_part["type"] != "uri":
            continue
        
        qid = value_part["value"].split("/")[-1]
        if qid in QIDS:
            continue # Removes duplicates
        QIDS.add(qid)

        label = part.get("valueLabel", {}).get("value", qid)
        type: str = part.get("valueTypeLabel", {}).get("value", "null")
        
        if type:
            type = type.title()
        # Sometimes no label is available so using q code allows us to try get a label    
        if is_qcode(label):
            label = lookup_label(qid, Q_CODE_PATH).title()

        nodes[qid] = {"label": label, "type": type}

        ### Edges
        source = source_qid  # the main entity queried
        target = qid
        prop_id = part["property"]["value"].split("/")[-1]

        prop_label: str = part.get("propertyLabel", {}).get("value", prop_id)
        # Again sometimes label isn't there so a straight lookup using the prop_id/p_code is used
        if is_pcode(prop_label.split("/").pop()):
            prop_label = lookup_label(prop_id, P_CODE_PATH).title()

        edges[source].append(
            {"target": target, "prop_id": prop_id, "prop_label": prop_label}
        )

    graph = {"nodes": nodes, "edges": edges}
    
    with open(DATA_PATH, "w") as f:
        json.dump(graph, f, indent=2)
