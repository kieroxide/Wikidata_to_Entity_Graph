from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from py.WikiGraph_Manager import WikiGraph_Manager
from py.Data_Handler import Data_Handler
from pathlib import Path

class WikiGraphServer:
    def __init__(self):
        self.app = Flask(__name__, static_folder='../frontend/')
        CORS(self.app)
        self.data_path = Path(__file__).parent / 'data'
        
        self.manager = WikiGraph_Manager()
        self.manager.change_json_dir(self.data_path)
    
        self.register_routes()
    
    def register_routes(self):
        """Register all Flask routes."""
        self.app.route('/data/<path:filename>')(self.serve_data)
        self.app.route('/api/graph/<entity_id>')(self.get_related_entities)
    
    def serve_data(self, filename):
        """View function to serve data directly from server to the frontend"""
        return send_from_directory(self.data_path, filename)

    def get_related_entities(self, entity_id):
        """Function to get related entities up to the passed limit and saves them to the json"""
        try:
            depth = request.args.get('depth', 1, type=int)
            relation_limit = request.args.get('relation_limit', 5, type=int)
            manager = WikiGraph_Manager()
            entities, properties, relations = manager.build(entity_id, depth, relation_limit)

            manager.save_all() # long-term cache will change to sql eventually
            return jsonify({"status"    : "ok",
                            "data"      :{
                                "entities"  : entities,
                                "properties": properties,
                                "relations" : relations }})
        except Exception as e:
            print(f"❌ Error processing {entity_id}: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
        
    def run(self, debug=True, port=5000):
        """Run the Flask server"""
        self.app.run(debug=debug, port=port)

server = WikiGraphServer()
server.run()