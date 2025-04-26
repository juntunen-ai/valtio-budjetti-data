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
        return jsonify(resp.json())
    except requests.exceptions.HTTPError as http_err:
        # Jos Tutkihallintoa API palauttaa 400/500, kerrotaan se suoraan asiakkaalle
        return jsonify({"error": f"HTTP error from upstream API: {str(http_err)}"}), resp.status_code if 'resp' in locals() else 502
    except requests.RequestException as e:
        # Muut virheet kuten timeout tms.
        return jsonify({"error": f"Request failed: {str(e)}"}), 502
    except Exception as e:
        # Yllättävät virheet
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

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