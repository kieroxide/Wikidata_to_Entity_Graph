from dataclasses import dataclass
from collections import defaultdict
from paths import Q_CODE_PATH
import requests
import json
import os
import re

@dataclass
class Node:
    qid: str
    label: str
    type: str

@dataclass
class Edge:
    source: str
    target: str
    type: str

def build_graph(data):
    data = data["results"]["bindings"]

    for part in data:
        # Skips any literals (non-entities)
        value_part = part["value"]
        if value_part["type"] != "uri":
            continue

        qid = value_part["value"].split("/")[-1]
        label = part.get("valueLabel", {}).get("value", qid)
        if(is_qcode(label)):
            label = lookup_label(qid)
        node = Node(qid, label, None)
        
        print(node)

def lookup_label(qid: str) -> str:
    """Looks for q_code in cached codes. if not found searches the API"""

    q_codes = load_q_codes()
    if qid in q_codes:
        return q_codes[qid]
    
    try:
        headers = {
            "User-Agent": "MyWikidataBot/1.0 (your_email@example.com)"
        }

        url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            print(f"Failed to fetch {qid}: status {r.status_code}")
            url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"

        entity = r.json()["entities"][qid]
        labels = entity.get("labels", {})

        if labels:
            label = next(iter(labels.values())).get("value", qid) # Looks for the first label
        else:
            label = qid

        q_codes[qid] = label
        # Saves the code to the json to cache and prevent using the API again
        with open(Q_CODE_PATH, "w") as f:
            json.dump(q_codes, f)
        return label

    except Exception as e:
        print(f"Error Occurred : {e}")

def load_q_codes():
    """Loads the q code cache from a file to prevent slow API calls"""
    if os.path.exists(Q_CODE_PATH):
        with open(Q_CODE_PATH, "r") as f:
            q_codes = json.load(f)
        return q_codes
    else:
        q_codes = defaultdict()
        with open(Q_CODE_PATH, "w") as f:
            json.dump(q_codes, f)

def is_qcode(value: str) -> bool:
    return bool(re.fullmatch(r"Q\d+", value))


def get_type():
    pass