"""
ValtioData-proxy – välittää ChatGPT-pluginin pyynnöt
Suomen valtiontalous-rajapintaan (budjettitaloudentapahtumat).

Käynnistyy Renderissä:  python proxy.py
"""

from flask import Flask, request, jsonify
import requests
import os

API_BASE = (
    "https://api.tutkihallintoa.fi/valtiontalous/v1/"
    "budjettitaloudentapahtumat"
)
TIMEOUT = 30  # sekuntia

app = Flask(__name__)


@app.get("/budjettidata")
def budget():
    """Välitä kaikki query-parametrit sellaisenaan ulkoiseen API:in."""
    qp = request.args.to_dict(flat=True)

    # Tarkistus: tyhjä pyyntö ei ole mielekäs
    if not qp:
        return (
            jsonify(
                {
                    "error": (
                        "Anna vähintään yksi rajausparametri "
                        "(esim. yearFrom, yearTo tai paaluokka)."
                    )
                }
            ),
            400,
        )

    try:
        resp = requests.get(API_BASE, params=qp, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        # Välitä virhekoodi ja viesti eteenpäin
        return jsonify({"error": str(e)}), 502

    return jsonify(resp.json())


@app.get("/")
def index():
    """Terveystsekki juuri-polussa."""
    return {"status": "ok", "service": "valtioData proxy"}, 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
