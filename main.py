from py.WikiGraph_Manager import WikiGraph_Manager
import requests
from urllib.parse import urlparse, unquote

def main():
    manager = WikiGraph_Manager()
    manager.build("Q1", 3)
    manager.save_all()

if __name__ == "__main__":
    main()
