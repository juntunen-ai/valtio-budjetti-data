from flask import Flask, request, jsonify, send_file
import requests
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

@app.get("/")
def index():
    return jsonify({"status": "ok", "service": "valtioData proxy"})

@app.get("/ai-plugin.json")
def serve_plugin_manifest():
    return send_file(os.path.join(BASE_DIR, "ai-plugin.json"), mimetype='application/json')

@app.get("/openapi.yaml")
def serve_openapi_spec():
    return send_file(os.path.join(BASE_DIR, "openapi.yaml"), mimetype='text/yaml')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port)
