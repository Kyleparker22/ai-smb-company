#!/usr/bin/env python3
"""Exit Radar — console server. Stdlib, localhost, port 8814 (launch name
`yourco-exit-radar`). Internal surface: the Founder + the agents. Nothing here sends
anything anywhere — see radar.py's docstring for the rails."""
import json
import re
import sys
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import radar

PORT = 8814


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(HERE), **k)

    def send_api(self, obj, code=200):
        raw = json.dumps(obj, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def body_json(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return {}

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/":
            self.path = "/console.html"
            return super().do_GET()
        if path == "/api/board":
            return self.send_api(radar.board())
        if path == "/api/export":
            return self.send_api({"sadie_json": radar.export_sadie_json(),
                                  "next": "save as exit-staged.json → "
                                          "python3 runtime/sourcing.py --sadie-json "
                                          "exit-staged.json --campaign 'Exit-flip'"})
        if not path.startswith("/api/"):
            return super().do_GET()
        return self.send_api({"error": "no route"}, 404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        body = self.body_json()
        if path == "/api/candidates":
            row, err = radar.add_candidate(body)
            return self.send_api({"candidate": row} if row else {"error": err},
                                 200 if row else 400)
        if path == "/api/candidates/import":
            rep, err = radar.import_candidates(body)
            return self.send_api({"report": rep} if rep else {"error": err},
                                 200 if rep else 400)
        m = re.match(r"^/api/candidates/([a-z0-9_]+)/stage$", path)
        if m:
            row, err = radar.set_stage(m.group(1), body.get("stage"),
                                       why=body.get("why"))
            return self.send_api({"candidate": row} if row else {"error": err},
                                 200 if row else 400)
        m = re.match(r"^/api/candidates/([a-z0-9_]+)/draft$", path)
        if m:
            rows = radar.load("candidates")
            c = next((x for x in rows if x["id"] == m.group(1)), None)
            if not c:
                return self.send_api({"error": "not found"}, 404)
            d, err = radar.draft_for(c)
            return self.send_api({"draft": d} if d else {"error": err},
                                 200 if d else 400)
        m = re.match(r"^/api/candidates/([a-z0-9_]+)/dnc$", path)
        if m:
            row, err = radar.mark_dnc(m.group(1))
            return self.send_api({"candidate": row} if row else {"error": err},
                                 200 if row else 400)
        return self.send_api({"error": "no route"}, 404)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    print(f"Exit Radar on http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
