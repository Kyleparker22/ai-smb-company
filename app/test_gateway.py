#!/usr/bin/env python3
"""Tests for the app gateway — every assertion here guards an ACCESS rule, not a feature.

Why this file exists, stated plainly: it should have been written first and wasn't. The repo
carries 207 assertions on HQ's honesty rules and 75 on agentops, and had ZERO on the 559-line
auth module and the 403-line gateway — the only components that decide who can read the CRM and
HQ. The role matrix was verified once, by hand, with curl, and the test accounts were deleted
afterwards. Nothing would have caught a later edit that moved the role check one line below the
proxy call.

Everything runs against a THROWAWAY auth store in a temp dir. The real store
(processes/partnerships/connector-console/_auth.json) is never opened, never written, and the
tests fail loudly if the environment override that guarantees that is missing.

Run:  python3 app/test_gateway.py
"""
import os, sys, tempfile, shutil, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# MUST happen before auth is imported — auth.py resolves its store dir at import time.
_STORE = tempfile.mkdtemp(prefix="yourco-gwtest-")
os.environ["YOURCO_CONNECTOR_AUTH_DIR"] = _STORE

sys.path.insert(0, os.path.join(ROOT, "processes", "partnerships", "connector-console"))
import auth  # noqa: E402

PASS = FAIL = 0
def ok(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL  {label}")

def section(t):
    print(f"\n{t}")


# ── guard: we are NOT pointed at the real store ─────────────────────────────
section("Test isolation")
ok(auth.DIR == _STORE, "auth resolves to the throwaway store, not the real one")
ok("connector-console" not in auth.DIR, "auth.DIR is nowhere near the live _auth.json")
ok(not os.path.exists(os.path.join(_STORE, "_auth.json")), "throwaway store starts empty")


# ── the role matrix — the actual security boundary ──────────────────────────
section("Role matrix (auth.ROLE_AREAS)")
MATRIX = {
    "partner":   {"hq": True,  "crm": True,  "console": True},
    "operator":  {"hq": True,  "crm": True,  "console": True},   # legacy alias for partner
    "advisor":   {"hq": False, "crm": True,  "console": True},   # NO HQ — runway, OA, splits
    "connector": {"hq": False, "crm": False, "console": True},
}
for role, areas in MATRIX.items():
    for area, allowed in areas.items():
        ok(auth.can_access(role, area) is allowed,
           f"{role} {'can' if allowed else 'CANNOT'} reach {area}")

ok(not auth.can_access("advisor", "hq"),
   "advisor is kept out of HQ — it carries runway, the OA and partner splits")

section("Deny by default")
for bogus in ("", None, "admin", "root", "Partner ", "PARTNER", "superuser", "../partner"):
    ok(auth.areas_for(bogus) == frozenset() or bogus.strip().lower() in auth.ROLE_AREAS,
       f"unknown role {bogus!r} grants nothing")
ok(auth.areas_for("nonexistent") == frozenset(), "an unknown role gets an EMPTY set, not a default")
ok(not auth.can_access(None, "hq"), "None role cannot reach HQ")
ok(not auth.is_console_admin("connector"), "a connector is not a console admin")
ok(auth.is_console_admin("operator"), "the legacy operator role still administers the console")

section("Every declared role is real and complete")
for r in auth.VALID_ROLES:
    ok(len(auth.areas_for(r)) > 0, f"declared role {r!r} grants at least one area")
ok(set(auth.ROLE_AREAS) == set(auth.VALID_ROLES), "VALID_ROLES and ROLE_AREAS agree")


# ── auth lifecycle ──────────────────────────────────────────────────────────
section("Auth lifecycle")
tok, _exp = auth.issue_setup_token("Test Partner", role="partner")
ok(bool(tok), "a setup token is issued")
bad, _n, _m = auth.complete_setup("not-a-real-token", "hunter2hunter2hunter2", "hunter2hunter2hunter2")
ok(bad is False, "a made-up setup token is refused")
done, _n, _m = auth.complete_setup(tok, "correct-horse-battery-staple-9", "correct-horse-battery-staple-9")
ok(done is True, "a real setup token completes")
spent, _n, _m = auth.complete_setup(tok, "another-passphrase-entirely-1", "another-passphrase-entirely-1")
ok(spent is False, "a setup token is SINGLE USE — replay is refused")

good, user, _ = auth.verify("Test Partner", "correct-horse-battery-staple-9")
ok(good is True and user["role"] == "partner", "correct passphrase verifies, carrying the role")
wrong, _u, _ = auth.verify("Test Partner", "wrong-passphrase")
ok(wrong is False, "wrong passphrase is refused")
nobody, _u, _ = auth.verify("Ghost Person", "correct-horse-battery-staple-9")
ok(nobody is False, "an account that does not exist is refused")

sid, csrf = auth.create_session("Test Partner", "partner")
ok(auth.session_for(sid)["role"] == "partner", "a session resolves to its role")
ok(auth.session_for("not-a-session-id") is None, "a forged session id resolves to nothing")
auth.destroy_session(sid)
ok(auth.session_for(sid) is None, "a destroyed session stops resolving")

section("Passphrase policy")
weak, _n, _m = auth.complete_setup(auth.issue_setup_token("Weak One", role="connector")[0], "short", "short")
ok(weak is False, "a too-short passphrase is refused")
mismatch_tok = auth.issue_setup_token("Mismatch One", role="connector")[0]
mm, _n, _m = auth.complete_setup(mismatch_tok, "correct-horse-battery-staple-9", "different-passphrase-here-7")
ok(mm is False, "a confirmation mismatch is refused")


# ── the gateway over real HTTP ──────────────────────────────────────────────
# Runs the actual server in-process on an ephemeral port. What is under test is the ROLE GATE:
# did the request get past it, or was it refused? The gate answers 403; anything else means the
# request was proxied onward.
#
# The status the backend then returns is NOT under test and must not be asserted on. The first
# version demanded exactly 502 ("no backends are started"), which made the suite depend on ambient
# machine state — it went red on 2026-08-23 purely because an HQ server was still running on :8791
# from an earlier session and answered 200. A test that flips on what else happens to be listening
# reports the wrong thing in both directions, so the assertion is allowed-vs-denied only.
section("Gateway over HTTP")
import json as _json, threading, http.client, socket, importlib.util

for name, role in (("Test Advisor", "advisor"), ("Test Connector", "connector")):
    t, _ = auth.issue_setup_token(name, role=role)
    auth.complete_setup(t, "correct-horse-battery-staple-9", "correct-horse-battery-staple-9")

_s = socket.socket(); _s.bind(("127.0.0.1", 0)); FREE = _s.getsockname()[1]; _s.close()
os.environ["YOURCO_APP_PORT"] = str(FREE)

spec = importlib.util.spec_from_file_location("gw", os.path.join(HERE, "server.py"))
gw = importlib.util.module_from_spec(spec); spec.loader.exec_module(gw)
srv = gw.Server(("127.0.0.1", FREE), gw.Gateway)
threading.Thread(target=srv.serve_forever, daemon=True).start()

def req(method, path, cookie=None, headers=None, body=None):
    c = http.client.HTTPConnection("127.0.0.1", FREE, timeout=10)
    h = dict(headers or {})
    if cookie: h["Cookie"] = cookie
    if body is not None: h.setdefault("Content-Type", "application/x-www-form-urlencoded")
    c.request(method, path, body=body, headers=h)
    r = c.getresponse(); data = r.read(); sc = r.status
    sk = r.getheader("Set-Cookie"); c.close()
    return sc, data, sk

def login(name):
    sc, _b, sk = req("POST", "/login", body=urllib.parse.urlencode(
        {"name": name, "passphrase": "correct-horse-battery-staple-9"}))
    return (sk.split(";")[0] if sk else None), sc

section("Unauthenticated access")
for p in ("/", "/hq/", "/crm/", "/connector/", "/hq/api/dashboard"):
    sc, _b, _ = req("GET", p)
    ok(sc == 303, f"{p} redirects to login when signed out (got {sc})")
sc, _b, _ = req("GET", "/login")
ok(sc == 200, "the login page itself is reachable signed out")
for p in ("/app.css", "/sw.js", "/manifest.webmanifest", "/icon.svg", "/healthz"):
    sc, _b, _ = req("GET", p)
    ok(sc == 200, f"{p} is served without auth (PWA needs it before sign-in)")

section("Bad credentials")
sc, _b, sk = req("POST", "/login", body=urllib.parse.urlencode(
    {"name": "Test Partner", "passphrase": "wrong"}))
ok(sc == 401, "wrong passphrase returns 401")
ok(not sk, "a failed login sets NO cookie")

section("Role gate over HTTP  (403 = denied; anything else = proxied onward)")
DENY = 403
EXPECT = {"Test Partner":   {"/hq/": "allow", "/crm/": "allow", "/connector/": "allow"},
          "Test Advisor":   {"/hq/": "deny",  "/crm/": "allow", "/connector/": "allow"},
          "Test Connector": {"/hq/": "deny",  "/crm/": "deny",  "/connector/": "allow"}}
for who, paths in EXPECT.items():
    ck, code = login(who)
    ok(bool(ck), f"{who} signs in (login returned {code})")
    for path, want in paths.items():
        sc, _b, _ = req("GET", path, cookie=ck)
        denied = (sc == DENY)
        got = "denied" if denied else f"proxied ({sc})"
        ok(denied == (want == "deny"), f"{who} is {'denied' if want == 'deny' else 'allowed'} at {path} — {got}")

section("Cross-origin POSTs are refused at the gateway")
ck, _ = login("Test Partner")
sc, _b, _ = req("POST", "/hq/api/hq-visit", cookie=ck,
                headers={"Origin": "https://evil.example"}, body="{}")
ok(sc == 403, f"a cross-origin POST is refused before it reaches a backend (got {sc})")
sc, _b, _ = req("POST", "/hq/api/hq-visit", cookie=ck,
                headers={"Origin": f"http://127.0.0.1:{FREE}"}, body="{}")
ok(sc != 403, f"a same-origin POST is NOT refused by the CSRF check (got {sc})")
sc, _b, _ = req("POST", "/hq/api/hq-visit", cookie=ck, body="{}")
ok(sc != 403, "a POST with no Origin header is allowed (same-origin forms often omit it)")

section("Session teardown")
ck, _ = login("Test Partner")
sc, _b, _ = req("GET", "/", cookie=ck); ok(sc == 200, "signed in, the shell renders")
req("GET", "/logout", cookie=ck)
sc, _b, _ = req("GET", "/", cookie=ck)
ok(sc == 303, "after logout the same cookie no longer works")

section("The shell only offers doors the role can reach")
ck, _ = login("Test Connector")
_sc, body, _ = req("GET", "/", cookie=ck)
html = body.decode("utf-8", "replace")
ok("/connector/" in html, "a connector is offered the console")
ok('href="/hq/"' not in html, "a connector is NOT offered HQ — the link is absent from the DOM")
ok('href="/crm/"' not in html, "a connector is NOT offered the CRM")

srv.shutdown()
shutil.rmtree(_STORE, ignore_errors=True)
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
