import os
import re
import json
from paths import Q_CODE_PATH

def save_to_cache(CACHE_PATH, id, label):
    cache = load_cache(CACHE_PATH)
    cache[id] = label
    # Saves the code to the json to cache and prevent using the API again
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f)

def load_cache(PATH):
    """Loads the cache from a file to prevent slow API calls"""
    
    if not os.path.exists("./jsons"):
        os.makedirs("./jsons")

    if os.path.exists(PATH):
        with open(PATH, "r") as f:
            cache = json.load(f)
    else:
        cache = {}
        with open(PATH, "w") as f:
            json.dump(cache, f)

    return cache


def is_qcode(value: str) -> bool:
    return bool(re.fullmatch(r"Q\d+", value))


def is_pcode(value: str) -> bool:
    return bool(re.fullmatch(r"P\d+", value))
