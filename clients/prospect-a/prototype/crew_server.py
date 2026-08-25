#!/usr/bin/env python3
"""
Crew-app backend — serves crew.html and persists field logs so every crew shares
one live picture (crew.html falls back to localStorage when this isn't running).

  GET  /                 -> crew.html
  GET  /api/state        -> {doors:[...], acks:{...}}
  POST /api/door         -> append a logged door  {crew,storm,address,status,amount,note,ts}
  POST /api/ack          -> set a crew's ack       {crew,storm,status}
  (static files served from this folder)

State persists to crew_state.json (gitignored). Field data flows into the
learning loop + ROI via rollup.py.

    python3 crew_server.py           # http://localhost:8798
"""
import json, os, http.server, socketserver

PORT = int(os.environ.get("CREW_PORT", "8798"))
STATE = os.path.join(os.path.dirname(__file__), "crew_state.json")

# Static allowlist: only the crew app's own web assets may be served. Everything else in this
# folder (crew_state.json, last_run.json, canvass_*.json, .env, *.py) holds PII/secrets → 404.
_SERVE_EXT = {".html", ".css", ".js", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".webp", ".woff", ".woff2"}


def _served_ok(path):
    if path in ("", "/"):
        return True
    if ".." in path:
        return False
    base = os.path.basename(path)
    if base.startswith("."):
        return False
    return os.path.splitext(base)[1].lower() in _SERVE_EXT


def load():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"doors": [], "acks": {}}


def store(s):
    json.dump(s, open(STATE, "w"), indent=2)


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=os.path.dirname(__file__), **k)

    def _json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        route = self.path.split("?")[0]
        if route == "/api/state":
            return self._json(load())
        if route == "/api/address":
            from urllib.parse import urlparse, parse_qs
            q = parse_qs(urlparse(self.path).query).get("q", [""])[0]
            try:
                import address
                return self._json(address.lookup(q) if q else {"error": "no query"})
            except Exception as e:
                return self._json({"error": str(e)}, 500)
        if self.path == "/":
            self.path = "/crew.html"
        # The static handler roots at this folder, which also holds crew_state.json (customer
        # addresses + job amounts), *_run.json, canvass_*.json and any .env. Serve ONLY the
        # crew web assets; 404 everything else so field data can't be downloaded unauthenticated.
        if not _served_ok(self.path.split("?")[0]):
            return self.send_error(404)
        return super().do_GET()

    def do_POST(self):
        route = self.path.split("?")[0]
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._json({"ok": False, "error": "bad json"}, 400)
        s = load()
        if route == "/api/door":
            data.setdefault("id", len(s["doors"]) + 1)
            s["doors"].insert(0, data)
        elif route == "/api/ack":
            s["acks"][f'{data.get("crew")}|{data.get("storm")}'] = {"status": data.get("status")}
        else:
            return self._json({"ok": False}, 404)
        store(s)
        return self._json({"ok": True})


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    # Localhost by default (house pattern: CRM_HOST / DASH_HOST). The crew app is the one
    # surface where phone-on-the-same-wifi access may be the point — set CREW_HOST=0.0.0.0
    # deliberately for that, rather than being exposed by default.
    HOST = os.environ.get("CREW_HOST", "127.0.0.1")
    with socketserver.TCPServer((HOST, PORT), H) as httpd:
        print(f"crew-app on http://{HOST}:{PORT}  (state -> crew_state.json)")
        httpd.serve_forever()
