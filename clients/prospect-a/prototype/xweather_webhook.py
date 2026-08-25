#!/usr/bin/env python3
"""
Xweather webhook receiver — push, not poll. Xweather POSTs storm reports + alerts
here the instant they're issued; we filter to what Nick wants and queue an
approval-gated alert. This is the real-time speed layer once his account has
webhooks enabled.

Nick's requested data (server-side filter applied here):
  · Alerts            — official watches/warnings (kept as-is)
  · Storm reports     — kept when they clear the thresholds below
  · Hail  ≥ 0.75"     (his "over 3/4 inch")
  · Wind  ≥ 55 mph
  · Tornado           — always

Xweather requires the receiver to return 202 immediately and process async, and
to authenticate via a shared secret (X-API-KEY header or ?secret=). Payload =
"same format the Xweather API returns" — the parser below is best-effort across
the common report/alert shapes; confirm field names against the first real
payload and adjust the two marked spots.

Setup: this must be reachable at a public HTTPS URL and registered with Xweather
(premium add-on — you give them the URL + datasets; see XWEATHER_WEBHOOK.md).

    XWEATHER_WEBHOOK_SECRET=... python3 xweather_webhook.py      # localhost:8799
"""
import json, os, http.server, socketserver
from urllib.parse import urlparse, parse_qs

PORT = int(os.environ.get("XW_WEBHOOK_PORT", "8799"))
SECRET = os.environ.get("XWEATHER_WEBHOOK_SECRET", "")
HAIL_MIN, WIND_MIN = 0.75, 55.0
STORE = os.path.join(os.path.dirname(__file__), "xweather_events.json")


def load():
    return json.load(open(STORE)) if os.path.exists(STORE) else {"events": []}


def save(s):
    json.dump(s, open(STORE, "w"), indent=2)


def _num(*vals):
    for v in vals:
        try:
            return float(v)
        except (TypeError, ValueError):
            continue
    return None


def normalize(item):
    """Best-effort across Xweather report/alert payload shapes. [CONFIRM #1: field
    names.] Returns a normalized event or None."""
    if not isinstance(item, dict):
        return None
    rep = item.get("report", item) if isinstance(item.get("report"), dict) else item
    det = item.get("detail", {}) if isinstance(item.get("detail"), dict) else {}
    place = item.get("place", {}) or {}
    loc = item.get("loc", {}) or {}
    kind = (rep.get("type") or rep.get("code") or item.get("dataset") or "").lower()
    when = item.get("dateTimeISO") or rep.get("dateTimeISO") or ""
    county = (place.get("county") or "").strip()
    latlon = [loc.get("lat"), loc.get("long")]

    if "alert" in kind or item.get("dataset") == "alerts" or rep.get("details"):
        title = rep.get("title") or det.get("name") or rep.get("name") or "Weather alert"
        return {"kind": "alert", "hazard": "alert", "label": title,
                "county": county, "time": when, "loc": latlon, "keep": True}
    if "hail" in kind:
        size = _num(det.get("size"), det.get("hailIN"), rep.get("size"))
        return {"kind": "report", "hazard": "hail", "value": size, "county": county,
                "time": when, "loc": latlon, "keep": size is not None and size >= HAIL_MIN}
    if "tor" in kind:
        return {"kind": "report", "hazard": "tornado", "county": county, "time": when,
                "loc": latlon, "keep": True}
    if "wind" in kind or "wnd" in kind:
        mph = _num(det.get("windSpeedMPH"), det.get("mag"), rep.get("windSpeedMPH"))
        return {"kind": "report", "hazard": "wind", "value": mph, "county": county,
                "time": when, "loc": latlon, "keep": mph is not None and mph >= WIND_MIN}
    return None


def handle(payload):
    # payload may be a single event or a collection under "response"/"reports"/"data"
    items = (payload.get("response") or payload.get("reports") or payload.get("data")
             or ([payload] if isinstance(payload, dict) else payload)) if isinstance(payload, dict) else payload
    kept = []
    for it in (items or []):
        ev = normalize(it)
        if ev and ev.get("keep"):
            kept.append(ev)
    if kept:
        s = load()
        s["events"] = kept + s["events"]
        s["events"] = s["events"][:500]
        save(s)
    return kept


class H(http.server.BaseHTTPRequestHandler):
    def _authed(self):
        if not SECRET:
            return True   # dev: no secret set
        hdr = self.headers.get("X-API-KEY") or self.headers.get("x-api-key")
        qs = parse_qs(urlparse(self.path).query).get("secret", [""])[0]
        return hdr == SECRET or qs == SECRET

    def do_POST(self):
        if not self._authed():
            self.send_response(401); self.end_headers(); return
        try:
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            self.send_response(202); self.end_headers(); return   # ack even on bad body
        # ack IMMEDIATELY (Xweather requirement), then process
        self.send_response(202); self.end_headers()
        try:
            kept = handle(payload)
            for e in kept:
                lbl = e.get("label") or (f'{e["hazard"]} {e.get("value","")}'.strip())
                print(f"⚡ Xweather → {e['hazard'].upper()}: {lbl} · {e.get('county','')} — queued (approval-gated)")
        except Exception as ex:
            print(f"  (process error: {ex})")

    def do_GET(self):
        # health + a peek at recent kept events
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "recent": load()["events"][:10]}).encode())

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), H) as httpd:
        print(f"Xweather webhook receiver on :{PORT}  (secret {'set' if SECRET else 'NOT set — dev only'}; "
              f"filters hail>={HAIL_MIN}\" wind>={WIND_MIN}mph)")
        httpd.serve_forever()
