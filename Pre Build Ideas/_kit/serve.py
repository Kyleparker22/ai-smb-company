#!/usr/bin/env python3
"""One localhost server for every pre-build vertical.

Serves the vertical's `app/` directory plus a JSON API built from a routes
table. Bound to 127.0.0.1 by construction — a demo build never listens on a
public interface (`localhost binding sweep`, 2026-08-13).

  routes = {("GET", "/api/board"): lambda q, b: {...},
            ("POST", "/api/approvals/decide"): lambda q, b: {...}}

A path segment written as `<id>` matches one segment and is passed in `q`.
Any read that cannot be computed returns `_missing`; the UI renders that
string and never renders a fake 0.

Stdlib only.
"""
import json, sys, urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

KIT = Path(__file__).resolve().parent


def _match(pattern, path):
    p, q = pattern.strip("/").split("/"), path.strip("/").split("/")
    if len(p) != len(q):
        return None
    out = {}
    for a, b in zip(p, q):
        if a.startswith("<") and a.endswith(">"):
            out[a[1:-1]] = urllib.parse.unquote(b)
        elif a != b:
            return None
    return out


def run(app_dir, routes, port, title, open_note=""):
    app_dir = Path(app_dir).resolve()

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(app_dir), **kw)

        def log_message(self, *a):
            pass

        # -- kit assets are shared, so serve them from the kit folder.
        #    Resolve and contain: a raw request can carry ".." (browsers
        #    normalize it away, http.client does not), and an unresolved
        #    join would serve files from anywhere above the kit.
        def translate_path(self, path):
            clean = urllib.parse.urlparse(path).path
            if clean.startswith("/_kit/"):
                target = (KIT / clean[len("/_kit/"):]).resolve()
                if str(target).startswith(str(KIT) + "/") or target == KIT:
                    return str(target)
                return str(KIT / "_refused_traversal")  # resolves to 404
            return super().translate_path(path)

        def _json(self, obj, code=200):
            body = json.dumps(obj, indent=1, default=str).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _dispatch(self, method):
            parsed = urllib.parse.urlparse(self.path)
            if not parsed.path.startswith("/api/"):
                return False
            q = {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}
            body = {}
            if method == "POST":
                n = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(n) if n else b""
                if raw:
                    try:
                        body = json.loads(raw)
                    except json.JSONDecodeError:
                        self._json({"error": "body was not JSON"}, 400)
                        return True
            for (m, pattern), fn in routes.items():
                if m != method:
                    continue
                params = _match(pattern, parsed.path)
                if params is None:
                    continue
                q.update(params)
                try:
                    self._json(fn(q, body))
                except Exception as e:  # a failure names itself; it never returns a 0
                    self._json({"error": f"{type(e).__name__}: {e}"}, 500)
                return True
            self._json({"error": f"no route for {method} {parsed.path}"}, 404)
            return True

        def do_GET(self):
            if not self._dispatch("GET"):
                super().do_GET()

        def do_POST(self):
            if not self._dispatch("POST"):
                self._json({"error": "not found"}, 404)

    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"{title} → http://127.0.0.1:{port}  (127.0.0.1 only){open_note}")
    sys.stdout.flush()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.server_close()
