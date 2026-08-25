#!/usr/bin/env python3
"""yourco CRM backend — serves the dashboard + a read/write API over crm/data.json.

Run locally:  python3 crm/server.py    then open  http://127.0.0.1:8790
- GET  /api/data     -> returns data.json (the source of truth)
- POST /api/data     -> overwrites data.json, regenerates data.js (static mirror)
- GET  /api/pending  -> returns _pending-activities.json (auto-logged activities awaiting confirm; [] if missing)
- POST /api/pending  -> overwrites _pending-activities.json (the UI removes items on confirm/dismiss)

Env (set on the VPS host; defaults keep local behavior identical):
- CRM_HOST     bind address (default 127.0.0.1; set 0.0.0.0 on the VPS so Tailscale can reach it)
- CRM_GIT_SYNC "1" to git-sync: pull-before-read (rate-limited) + commit/push-after-write,
               so hosted phone edits and the agents' edits stay in sync via the repo. Off locally.
- YOURCO_DATA_ROOT  the Playground switch (2026-08-07). Points DATA at a parallel tree
               (`playground/crm/data.json`) while CODE and STATIC ASSETS stay here, so the
               playground always runs the REAL current CRM against synthetic data and can
               never drift into a stale fork. Unset = live. See `playground/_README.md`.
"""
import json, os, sys, time, subprocess, http.server, socketserver
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# --- data root -------------------------------------------------------------
# Code lives at HERE and never moves. Only the DATA root is overridable, which is the whole
# isolation model: same server, same HTML, different data. A playground that copied the code
# would start drifting the day either side changed — the failure CLAUDE.md calls the #1
# cross-session bug — so it deliberately cannot.
DATA_ROOT = os.environ.get("YOURCO_DATA_ROOT") or REPO
PLAYGROUND = bool(os.environ.get("YOURCO_DATA_ROOT"))
DATA_DIR = os.path.join(DATA_ROOT, "crm") if PLAYGROUND else HERE
if PLAYGROUND:
    os.makedirs(DATA_DIR, exist_ok=True)

try:  # shared brain (lives in dashboard/) — powers outreach drafting. Optional.
    sys.path.insert(0, os.path.join(REPO, "dashboard"))
    import melanie
except Exception:
    melanie = None
DATA = os.path.join(DATA_DIR, "data.json")
DATA_JS = os.path.join(DATA_DIR, "data.js")
PENDING = os.path.join(DATA_DIR, "_pending-activities.json")  # auto-logged activities awaiting human confirm
PORT = int(os.environ.get("PORT", 8790))  # PORT env lets the Cowork preview assign a port
HOST = os.environ.get("CRM_HOST", "127.0.0.1")
MAX_BODY = 2 * 1024 * 1024  # 2 MB cap on request bodies (anti-DoS)
# Playground never syncs to git, whatever the env says — a sandbox that can commit is not a
# sandbox. This is a hard override, not a default.
GIT_SYNC = os.environ.get("CRM_GIT_SYNC") == "1" and not PLAYGROUND

_last_pull = [0.0]
PULL_EVERY = 20  # seconds — rate-limit pull-on-read

# The insight layer: seven modules that read the CRM (and its git history) and answer
# questions a CRM row can't. Each exposes compute(); ghost reads git and self-caches.
# Served under /api/insight/<key> so the dashboard fetches them without a page reload.
INSIGHTS = ("ghost", "spread", "warmpath", "calibration", "mirror", "autonomy", "promises",
            "expansion", "price", "autopsy", "capacity", "decisions", "antipipeline",
            "disputes", "blocks", "conversation", "enrichment")
_insight_cache = {}
INSIGHT_TTL = {"ghost": 300, "spread": 60, "warmpath": 60, "calibration": 30,
               "mirror": 15, "autonomy": 30, "promises": 30, "expansion": 60,
               "price": 30, "autopsy": 30, "capacity": 30, "antipipeline": 30,
               "disputes": 30, "blocks": 300, "conversation": 15, "enrichment": 60,
               # decision P&L walks git for the ghost timeline — same cost as ghost itself
               "decisions": 300}
# Insight key -> (module, callable). Only needed where they differ from the key.
INSIGHT_IMPL = {"price": ("pricing_power", "compute"), "autopsy": ("autopsy", "compute"),
                "capacity": ("capacity", "compute"), "decisions": ("decision_pl", "compute"),
                "antipipeline": ("antipipeline", "compute"),
                "disputes": ("counterparty", "disputes"), "blocks": ("blocks", "registry"),
                "conversation": ("conversation", "compute"),
                "enrichment": ("enrich_waterfall", "compute")}
# /api/history — a past state of data.json out of git, keyed by days-back. Separate from the
# insight cache because it is a raw blob, not a computed read, and it shells out to git.
_HISTORY_CACHE = {}


def insight(key, fresh=False):
    """Compute one insight, memoized briefly so a dashboard render doesn't re-walk git."""
    now = time.time()
    hit = _insight_cache.get(key)
    if hit and not fresh and now - hit[0] < INSIGHT_TTL.get(key, 60):
        return hit[1]
    sys.path.insert(0, HERE)
    if key == "ghost":
        # The refusal itself lives in ghost.compute() as of 2026-08-24, so the CLI and any future
        # caller inherit it too — this route used to hold the only copy, which left
        # `YOURCO_DATA_ROOT=… python3 crm/ghost.py` replaying live history inside the sandbox.
        # Kept as an early return so the sandbox never even imports the module.
        import ghost
        if PLAYGROUND:
            return dict(ghost.PLAYGROUND_REFUSAL)
        out = ghost.compute(fresh=fresh)
    else:
        with open(DATA) as f:
            data = json.load(f)
        if key == "spread":
            import adversarial
            out = adversarial.compute(data)
        elif key == "warmpath":
            import warmpath
            out = warmpath.compute(data)
        elif key == "calibration":
            import calibration
            out = calibration.compute(data)
        elif key == "mirror":
            import mirror
            out = mirror.compute(data)
        elif key == "autonomy":
            import autonomy
            out = autonomy.compute(data)
        elif key == "expansion":
            import expansion
            out = expansion.compute(data)
        elif key == "promises":
            import promises
            out = promises.compute(data)
            try:
                with open(os.path.join(DATA_DIR, "_promise-candidates.json")) as f:
                    out["candidates"] = json.load(f).get("candidates", [])
            except Exception:
                out["candidates"] = []
        elif key in INSIGHT_IMPL:
            # The modules added 2026-08-13 all follow one shape, so they resolve through a
            # table instead of another elif. A new insight is a row here, not a code branch.
            modname, fnname = INSIGHT_IMPL[key]
            mod = __import__(modname)
            fn = getattr(mod, fnname)
            import inspect
            # Match on the parameter NAME, not merely on "has a positional arg". decision_pl's
            # first param is `top` (a row limit) — passing the dataset into it raised
            # "int() argument must be a string" and the endpoint 500'd. Positional dispatch by
            # position is a guess; by name it is a contract.
            names = list(inspect.signature(fn).parameters)
            out = fn(data) if names and names[0] == "data" else fn()
        else:
            raise KeyError(key)
    _insight_cache[key] = (now, out)
    return out


def write_mirror(data):
    if melanie:  # one canonical implementation lives in melanie.write_mirror
        return melanie.write_mirror(data)
    with open(DATA_JS, "w") as f:
        f.write("/* AUTO-GENERATED from data.json by server.py. Source of truth is data.json. */\n")
        f.write("window.CRM_DATA = " + json.dumps(data, indent=2) + ";\n")


def _git(*args, timeout=60):
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True, timeout=timeout)


def git_pull_throttled():
    if not GIT_SYNC:
        return
    now = time.time()
    if now - _last_pull[0] < PULL_EVERY:
        return
    _last_pull[0] = now
    try:
        _git("pull", "--rebase", "--autostash", "--quiet", timeout=30)
    except Exception:
        pass  # best-effort; never break a read on a git hiccup


def git_push_data():
    if not GIT_SYNC:
        return
    try:
        _git("add", "crm/data.json", "crm/data.js")
        r = _git("commit", "-m", "CRM edit via hosted UI [skip-loop]")
        if r.returncode == 0:  # only push if something committed
            _git("pull", "--rebase", "--autostash", "--quiet", timeout=30)  # avoid non-fast-forward vs loop pushes
            _git("push", "--quiet", timeout=60)
    except Exception:
        pass


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=HERE, **k)

    def end_headers(self):  # never serve a stale dashboard from browser cache
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_guarded(self):
        """Size-cap + same-origin (CSRF) guard on mutating requests. Returns body bytes, or None after writing an error."""
        try:
            n = int(self.headers.get("Content-Length", 0))
        except ValueError:
            n = 0
        if n > MAX_BODY:
            self._json(413, {"error": "request too large"}); return None
        origin = self.headers.get("Origin")
        if origin and urlparse(origin).netloc != self.headers.get("Host", ""):
            self._json(403, {"error": "cross-origin request blocked"}); return None
        return self.rfile.read(n)

    def do_GET(self):
        p = urlparse(self.path)
        if p.path == "/api/mode":  # lets the UI render the playground banner
            return self._json(200, {"playground": PLAYGROUND, "dataRoot": DATA_ROOT if PLAYGROUND else None})
        if p.path.startswith("/api/insight/"):
            key = p.path.rsplit("/", 1)[-1]
            if key not in INSIGHTS:
                return self._json(404, {"error": f"unknown insight '{key}'", "available": list(INSIGHTS)})
            try:
                return self._json(200, insight(key, fresh="fresh=1" in (p.query or "")))
            except Exception as e:
                # An insight failing must never take the dashboard down — it degrades to absent.
                return self._json(200, {"_error": f"{type(e).__name__}: {e}", "_insight": key})
        if p.path == "/api/history":
            # The CRM as it stood N days ago, straight out of git. The UI runs the SAME KPI
            # function over this blob and over today's, so a metric can never disagree with
            # its own history. Cached briefly — it shells out to git.
            try:
                days = int(dict(pq.split("=", 1) for pq in (p.query or "").split("&")
                                if "=" in pq).get("days", 30))
            except Exception:
                days = 30
            days = max(1, min(365, days))
            now = time.time()
            hit = _HISTORY_CACHE.get(days)
            if hit and now - hit[0] < 300:
                return self._json(200, hit[1])
            try:
                import history
                r = history.compute(days)
            except Exception as e:
                return self._json(200, {"found": False, "why": f"{type(e).__name__}: {e}"})
            _HISTORY_CACHE[days] = (now, r)
            return self._json(200, r)
        if urlparse(self.path).path == "/api/heat":
            # Artifact telemetry rollup: sessions/last-seen/minutes per served path, for the
            # deal dossiers. Beacons land in telemetry.jsonl via POST /t (see below).
            try:
                rows = {}
                tf = os.path.join(DATA_DIR, "telemetry.jsonl")
                if os.path.exists(tf):
                    with open(tf) as f:
                        for line in f:
                            try:
                                ev = json.loads(line)
                            except Exception:
                                continue
                            p = str(ev.get("p", ""))[:200]
                            r = rows.setdefault(p, {"views": 0, "beats": 0, "last": "", "sessions": set()})
                            if ev.get("e") == "view":
                                r["views"] += 1
                            else:
                                r["beats"] += 1
                            r["last"] = max(r["last"], str(ev.get("ts", ""))[:19])
                            if ev.get("s"):
                                r["sessions"].add(str(ev.get("s"))[:40])
                out = {p: {"views": r["views"], "minutes": round(r["beats"] * 15 / 60, 1),
                           "last": r["last"], "sessions": len(r["sessions"])} for p, r in rows.items()}
                return self._json(200, out)
            except Exception as e:
                return self._json(200, {"_error": str(e)})
        if urlparse(self.path).path == "/api/pending":
            try:
                items = []
                if os.path.exists(PENDING):
                    with open(PENDING) as f:
                        items = json.load(f)
                if not isinstance(items, list):
                    items = []
                return self._json(200, items)
            except Exception:
                return self._json(200, [])  # a corrupt/missing queue never breaks the dashboard
        if urlparse(self.path).path == "/api/data":
            git_pull_throttled()
            try:
                with open(DATA) as f:
                    data = json.load(f)
                # Stamp the revision the client is loading from. It rides back verbatim in the
                # POST body (JSON.stringify(D)), letting the server reject a stale save (409)
                # instead of silently overwriting an edit another writer made in between.
                if isinstance(data, dict) and melanie:
                    data["_rev"] = melanie.crm_rev()
                return self._json(200, data)
            except Exception as e:
                return self._json(500, {"error": str(e)})
        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/t":
            # Artifact beacon — cross-origin by design (demo pages on other ports post here).
            # Append-only, size-capped, no read-back: safe to exempt from the same-origin guard.
            # Disclosure ships on the demo pages ("we see when our demos are viewed").
            try:
                n = min(int(self.headers.get("Content-Length", 0) or 0), 4096)
                ev = json.loads(self.rfile.read(n) or b"{}")
                rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                       "p": str(ev.get("p", ""))[:200], "e": str(ev.get("e", "view"))[:10],
                       "s": str(ev.get("s", ""))[:40]}
                with open(os.path.join(DATA_DIR, "telemetry.jsonl"), "a") as f:
                    f.write(json.dumps(rec) + "\n")
                body = b'{"ok":true}'
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception:
                self.send_response(204); self.end_headers()
            return
        if path not in ("/api/draft", "/api/enrich", "/api/data", "/api/pending", "/api/promise-scan"):
            return self.send_error(404)
        body = self._read_guarded()
        if body is None:
            return
        if path == "/api/promise-scan":  # propose promise candidates from activities + client docs
            try:
                sys.path.insert(0, HERE)
                import promises as _pm
                with open(DATA) as f:
                    data = json.load(f)
                cands = _pm.scan(data)
                _pm.save_candidates(cands)
                _insight_cache.pop("promises", None)
                return self._json(200, {"ok": True, "candidates": cands})
            except Exception as e:
                return self._json(500, {"error": str(e)})
        if path == "/api/pending":  # overwrite the pending queue (the UI posts the remaining items on confirm/dismiss)
            try:
                items = json.loads(body or b"[]")
                if not isinstance(items, list):
                    return self._json(400, {"error": "expected a list of pending activities"})
                if melanie:  # serialize with the other CRM writers via the shared lock
                    with melanie.crm_lock():
                        melanie._atomic_dump(PENDING, items)
                else:  # bare local run — still atomic
                    tmp = f"{PENDING}.tmp.{os.getpid()}"
                    with open(tmp, "w") as f:
                        json.dump(items, f, indent=2)
                    os.replace(tmp, PENDING)
                return self._json(200, {"ok": True, "n": len(items)})
            except json.JSONDecodeError:
                return self._json(400, {"error": "bad request"})
            except Exception as e:
                return self._json(500, {"error": str(e)})
        if path == "/api/enrich":  # read a prospect's public site → fill CRM gaps (paid + fetch → rate-limit)
            if melanie and not melanie._rate_ok():
                return self._json(429, {"error": "rate limited"})
            try:
                req = json.loads(body or b"{}")
            except Exception:
                return self._json(400, {"error": "bad request"})
            if not melanie:
                return self._json(200, {"error": "enrich unavailable (brain not loaded)"})
            if req.get("all"):  # bulk: enrich every prospect missing email/location + write the CRM
                res = melanie.bulk_enrich()
                git_push_data()  # persist the filled CRM if hosted (no-op locally)
                return self._json(200, res)
            return self._json(200, melanie.enrich(req.get("company", "")))
        if path == "/api/draft":  # Reilly drafts a first-touch outreach (paid → rate-limit)
            if melanie and not melanie._rate_ok():
                return self._json(429, {"text": "", "error": "rate limited"})
            try:
                req = json.loads(body or b"{}")
            except Exception:
                return self._json(400, {"error": "bad request"})
            if not melanie:
                return self._json(200, {"text": "", "error": "drafting unavailable (brain not loaded)"})
            try:
                text = melanie.draft(req.get("company", ""), referred_by=req.get("referredBy", ""))
            except TypeError:  # older melanie without the referred_by param
                text = melanie.draft(req.get("company", ""))
            return self._json(200, {"text": text or ""})
        # /api/data — overwrite the CRM (validated shape), guarded against stale-save clobber
        try:
            data = json.loads(body)
            if not isinstance(data, dict) or "companies" not in data:
                return self._json(400, {"error": "expected a CRM object"})
            client_rev = data.pop("_rev", None)  # never persist the token
            if melanie:
                # Serialize with Melanie's own writes and reject a save built on stale data.
                with melanie.crm_lock():
                    if client_rev is not None and client_rev != melanie.crm_rev():
                        return self._json(409, {"error": "stale — the CRM changed since you loaded it; "
                                                          "reload and re-apply your edit"})
                    melanie._atomic_dump(DATA, data)
                    write_mirror(data)
                    new_rev = melanie.crm_rev()  # under the lock, before any git op moves the file
            else:  # brain not loaded (bare local run) — atomic write, no cross-process guard
                tmp = f"{DATA}.tmp.{os.getpid()}"
                with open(tmp, "w") as f:
                    json.dump(data, f, indent=2)
                os.replace(tmp, DATA)
                write_mirror(data)
                new_rev = str(os.stat(DATA).st_mtime_ns)
            git_push_data()
            # Return the new rev so the client updates its baseline — otherwise the same user's
            # next save would false-409 against their own just-written change.
            return self._json(200, {"ok": True, "_rev": new_rev})
        except Exception as e:
            return self._json(500, {"error": str(e)})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
        where = "Tailscale + localhost" if HOST == "0.0.0.0" else HOST
        print(f"yourco CRM running -> http://{HOST}:{PORT}  (bind: {where}; git-sync: {GIT_SYNC})")
        httpd.serve_forever()
