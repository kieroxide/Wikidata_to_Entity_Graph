from py.WikiGraph_Manager import WikiGraph_Manager
import requests
from urllib.parse import urlparse, unquote

def main():
    manager = WikiGraph_Manager()
    manager.build("Q1", 15)
    manager.save_all()
    manager.test_clean_results()
    manager.test_results(console=True)

if __name__ == "__main__":
    main()
