from collections import defaultdict
import os
import re
import requests
import json


def lookup_label(id: str, CACHE_PATH) -> str:
    """Looks for codes in cached codes. if not found searches the API"""

    cache = load_cache(CACHE_PATH)
    if id in cache:
        return cache[id]

    try:
        headers = {"User-Agent": "MyWikidataBot/1.0 (kieroxide - github BOT)"}

        url = f"https://www.wikidata.org/wiki/Special:EntityData/{id}.json"
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            print(f"Failed to fetch {id}: status {r.status_code}")
            url = f"https://www.wikidata.org/wiki/Special:EntityData/{id}.json"

        entity = r.json()["entities"][id]
        labels = entity.get("labels", {})
        
        #ignore non english labels and just use id as label
        label = labels["en"]["value"] if "en" in labels else id 

        # Saves the code to the json to cache and prevent using the API again
        with open(CACHE_PATH, "w") as f:
            json.dump(cache, f)
        return label

    except Exception as e:
        print(f"Error Occurred : {e}")


def load_cache(PATH):
    """Loads the cache from a file to prevent slow API calls"""
    
    if not os.path.exists("./jsons"):
        os.makedirs("./jsons")

    if os.path.exists(PATH):
        with open(PATH, "r") as f:
            cache = json.load(f)
    else:
        cache = defaultdict()
        with open(PATH, "w") as f:
            json.dump(cache, f)

    return cache


def is_qcode(value: str) -> bool:
    return bool(re.fullmatch(r"Q\d+", value))


def is_pcode(value: str) -> bool:
    return bool(re.fullmatch(r"P\d+", value))
