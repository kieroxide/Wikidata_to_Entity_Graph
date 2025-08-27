TOP_X_PROPERTIES_QUERY = ["""
        SELECT ?property ?propertyLabel (COUNT(?value) AS ?count)
            WHERE {
              wd:""", None,""" ?property ?value .
              SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }
            GROUP BY ?property ?propertyLabel
            ORDER BY DESC(?count)
            LIMIT """, None]

def build_property_query(QID: str, LIMIT: str):
    """Returns top {LIMIT} properties of wikidata item QID"""
    query = ""
    to_insert = [QID, LIMIT]
    for part in TOP_X_PROPERTIES_QUERY:
        if(part == None):
            part = to_insert.pop(0)
        query += part
    return query

PROPERTY_DETAILS_QUERY = ["""SELECT ?property ?propertyLabel ?value ?valueLabel
    WHERE {
      wd:""", None,""" ?property ?value .
      VALUES ?property {""", None,"""}
      
      FILTER(isURI(?value))
      
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }"""]

def build_property_details_query(QID: str, PROPERTIES_RAW: dict):
    """Returns top {LIMIT} properties of wikidata item QID"""
    query = ""
    P_IDs = get_PIDS(PROPERTIES_RAW)
    P_IDs = " ".join(list(P_IDs))
    to_insert = [QID, P_IDs]
    for part in PROPERTY_DETAILS_QUERY:
        if(part == None):
            part = to_insert.pop(0)
        query += part
    return query

def get_PIDS(PROPERTIES_RAW: dict):
    pids = set()
    RESULTS = PROPERTIES_RAW.get("results")

    for prop in RESULTS.get("bindings"):
        url: str = prop["property"]["value"]
        pid = url.split("/").pop()

        if pid[0] != 'P':
            continue
        pids.add("wdt:" + pid)

    return pids