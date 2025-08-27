from query_builder import build_property_query, build_property_details_query
from API import execute_query
def main():
    QID = "Q193581"
    LIMIT = "100"
    p_query = build_property_query(QID, LIMIT)
    p_res = execute_query(p_query)
    p_d_query = build_property_details_query(QID, p_res)
    print(p_d_query)
    p_d_res = execute_query(p_d_query)
    print(p_d_res)

main()