"""
ValtioData-proxy – välittää ChatGPT-pluginin pyynnöt
Suomen valtiontalous-rajapintaan (budjettitaloudentapahtumat).

Käynnistyy Renderissä:  python proxy.py
"""

import http.server
import socketserver
import urllib.request
import urllib.parse
import json

API_BASE = (
    "https://api.tutkihallintoa.fi/valtiontalous/v1/"
    "budjettitaloudentapahtumat"
)


class BudgetHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)

        if parsed_url.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"status": "ok", "service": "valtioData proxy"}
            self.wfile.write(json.dumps(response).encode())
        elif parsed_url.path == "/budjettidata":
            query_params = urllib.parse.parse_qs(parsed_url.query)

            if not query_params:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {
                    "error": (
                        "Anna vähintään yksi rajausparametri "
                        "(esim. yearFrom, yearTo tai paaluokka)."
                    )
                }
                self.wfile.write(json.dumps(response).encode())
                return

            target_url = API_BASE + "?" + urllib.parse.urlencode(query_params, doseq=True)
            try:
                with urllib.request.urlopen(target_url) as resp:
                    data = resp.read().decode()
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(data.encode())
            except urllib.error.HTTPError as e:
                self.send_response(502)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"error": str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            super().do_GET(self)


PORT = 8080
with socketserver.TCPServer(("", PORT), BudgetHandler) as httpd:
    httpd.serve_forever()
