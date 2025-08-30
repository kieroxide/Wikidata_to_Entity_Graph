import json
from collections import defaultdict
import requests
from paths import Q_CODE_PATH, P_CODE_PATH, DATA_PATH
from cache import is_pcode, is_qcode, save_to_cache, load_cache
from query_builder import build_property_query, build_property_details_query
from API import execute_query
from time import sleep
import utils

class Graph:
    def __init__(self):
        self.vertices = {}
        self.edges = defaultdict(list)

    def change_vertex_label(self, id, new_label):
        self.vertices[id]["label"] = new_label
       
    def change_edge_label(self, source_id, edge_id, new_label):
        for edge in self.vertices[source_id]:
            if edge["target"] == edge_id:
                edge["prop_label"] = new_label

    def lookup_label_from_cache(self, CACHE_PATH, ids: list, source_id= None):
        cache = load_cache(CACHE_PATH)
        remaining = []
        for id in ids:
            if id in cache:
                if CACHE_PATH == Q_CODE_PATH:
                    self.vertices[id]["label"] = cache[id]
                else:
                    self.edges[source_id]["prop_label"] = cache[id]
            else:
                remaining.append(id)
        return ids
    
    def lookup_labels_from_API(self, CACHE_PATH, ids):
        if not ids:
            return
        for batch_ids in utils.chunked(ids, 50): # Max size of wikidata request is 50
            ids_str_query = "|".join(batch_ids) # We can query multiple ids at once using | 
            headers = {"User-Agent": "MyWikidataBot/1.0 (kieroxide - github BOT)"}

            url = (
            "https://www.wikidata.org/w/api.php"
            f"?action=wbgetentities&ids={ids_str_query}&format=json"
            )
            r = requests.get(url, headers=headers)

            if r.status_code != 200:
                print(f"Failed to fetch {ids_str_query}: status {r.status_code}")


            data = r.json()
            try:
                entities = data["entities"]
            except:
                print(data)
            for id in batch_ids:
                entity: dict = entities[id]
                labels = entity["labels"]
                if "en" in labels:
                    label = labels["en"]["value"]
                    self.change_vertex_label(id, label)
                    save_to_cache(CACHE_PATH, id, label)
            
    def expand_graph(self, source_qid, data=None, limit=10, depth=0, maxDepth=0):
        if data is None:
            p_query = build_property_query(source_qid, limit)
            p_res = execute_query(p_query)
            p_d_query = build_property_details_query(source_qid, p_res)
            data = execute_query(p_d_query)
        
        try:
            data = data["results"]["bindings"]
        except:
            print(data)
            print(type(data))
            

        QIDS = set()
        vertices = {}
        edges = defaultdict(list)

        for part in data:
            ### Vertices
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
                continue  # Removes duplicates
            QIDS.add(qid)

            label = part.get("valueLabel", {}).get("value", qid)
            entity_type: str = part.get("valueTypeLabel", {}).get("value", "null")

            if entity_type:
                entity_type = entity_type.title()
            # Sometimes no label is available so using q code allows us to try get a label
            #if is_qcode(label):
            #    label = lookup_label(qid, Q_CODE_PATH).title()
            #    self.lookup_label_from_API()

            vertices[qid] = {"label": label, "type": entity_type}

            ### Edges
            source = source_qid  # the main entity queried
            target = qid
            prop_id = part["property"]["value"].split("/")[-1]

            prop_label: str = part.get("propertyLabel", {}).get("value", prop_id)
            #PIDS["Source"] = qid
            #PIDS[""]
            #PIDS["Edge_Label"] = prop_label

            # Again sometimes label isn't there so a straight lookup using the prop_id/p_code is used
            #if is_pcode(prop_label.split("/").pop()):
            #    prop_label = lookup_label(prop_id, P_CODE_PATH)
#
            if prop_label:
                prop_label = prop_label.title()
                
            edges[source].append(
                {target : {"prop_id": prop_id, "prop_label": prop_label}}
            )

        self.add_vertices(vertices)
        self.add_edges(edges)
        
        no_label_QIDS = []
        for QID in QIDS:
            if is_qcode(QID):
                no_label_QIDS.append(QID)
        no_label_QIDS = self.lookup_label_from_cache(Q_CODE_PATH, no_label_QIDS)
        self.lookup_labels_from_API(Q_CODE_PATH, no_label_QIDS)


        

        depth += 1
        if depth >= maxDepth:
            return
        for QID in QIDS:
            self.expand_graph(QID)

    def add_vertices(self, vertices: dict):
        self.vertices.update(vertices)


    def add_edges(self, edges: dict):
        for source, edge_list in edges.items():
            self.edges[source].extend(edge_list)

    def toObject(self) -> dict:
        return {
            "vertices": self.vertices,
            "edges": {k: v for k, v in self.edges.items()} # converts default dict -> to dict
        }

    def save_to_json(self, path) -> bool:
        """Converts graph to object and json dumps the object to file at path
        Returns bool for success checking"""
        try:
            with open(path, "w") as f:
                json.dump(self.toObject(), f, indent=2)
            return True

        except Exception as e:
            print(f"Error writing graph to file. Error {e}")
            return False
