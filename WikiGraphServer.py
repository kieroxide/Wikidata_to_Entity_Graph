from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from py.WikiGraph_Manager import WikiGraph_Manager
from pathlib import Path
import os

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
            entities, properties, relations = self.manager.build(entity_id, depth, relation_limit)
            
            return jsonify({"status": "ok", "data": {"entities": entities, "properties": properties, "relations": relations}})
        except Exception as e:
            print(f"❌ Error processing {entity_id}: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    def run(self, debug=True, port=None):
        """Run the Flask server"""
        port = port or int(os.environ.get("PORT", 5000))
        debug = debug if "PORT" not in os.environ else False
        self.app.run(debug=debug, host="0.0.0.0", port=port)

# Expose app for Gunicorn
server = WikiGraphServer()
app = server.app

if __name__ == "__main__":
    server.run()