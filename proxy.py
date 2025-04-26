from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__)

API_BASE = "https://api.tutkihallintoa.fi/valtiontalous/v1/budjettitaloudentapahtumat"
TIMEOUT = 30

@app.get("/budjettidata")
def budget():
    qp = request.args.to_dict(flat=True)
    if not qp:
        return jsonify({"error": "Missing query parameters"}), 400
    try:
        resp = requests.get(API_BASE, params=qp, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 502
    return jsonify(resp.json())

# NEW: Root route
@app.get("/")
def index():
    return jsonify({"status": "ok", "service": "valtioData proxy"})

# NEW: Serve ai-plugin.json
@app.get("/ai-plugin.json")
def serve_plugin_manifest():
    return send_from_directory(directory='.', path="ai-plugin.json", mimetype='application/json')

# NEW: Serve openapi.yaml
@app.get("/openapi.yaml")
def serve_openapi_spec():
    return send_from_directory(directory='.', path="openapi.yaml", mimetype='text/yaml')

app = Flask(__name__)

port = int(os.environ.get('PORT', 8080))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
