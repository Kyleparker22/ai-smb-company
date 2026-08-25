#!/usr/bin/env python3
"""yourco — the app gateway. One login, one address, three surfaces behind it.

WHY THIS EXISTS
  HQ, the CRM and the Connector Console are three separate stdlib servers on three ports.
  Two of them have NO authentication at all — verified 2026-08-23: an unauthenticated
  GET to :8790/api/data returns the entire CRM, every prospect's name and number. They are
  safe today only because they bind to 127.0.0.1 and are reached over Tailscale. Network
  position is the whole security model, and "the team can log in" is incompatible with it.

  So: one gateway owns identity, and the three apps stay exactly as they are.

WHAT IT DOES NOT DO
  It does not rewrite the apps. HQ and the CRM are ~7,500 lines of working UI between them
  and touching that to add auth would be the riskiest change in this repo. Instead the
  gateway reverse-proxies them and injects a three-line fetch shim, because a measurement
  said it could: both UIs reach their APIs *only* through fetch() with absolute paths —
  no XMLHttpRequest, no EventSource, no absolute href or src. The console additionally
  emits ~10 absolute href/action attributes, which are rewritten on the way out.

ROLES  (auth.ROLE_AREAS is the authority; this file only enforces it)
  partner    HQ + CRM + Console      the 50/35/15 members
  advisor    CRM + Console           yourco salespeople — no HQ: it carries runway,
                                     the OA, partner splits and the finance model
  connector  Console only            external referral partners

SINGLE SIGN-ON, FOR FREE
  The gateway and the console share auth.py AND its session store, so the gateway sets the
  same `yourco_console` cookie the console already understands. Proxying the cookie through
  means the console recognises the session and never shows its own login. No token passing,
  no second identity system.

SECURITY POSTURE — read before exposing this
  The three backends MUST stay bound to 127.0.0.1. The gateway is the only process that may
  ever listen on a public interface, and it is therefore a single point of failure: a routing
  bug here is full exposure of everything. That is an accepted, deliberate trade against the
  alternative (bolting auth onto three codebases), and it is why the role check happens before
  the proxy call rather than inside it.

  ⚠️ Nothing here is exposed publicly yet. Public exposure is an external surface and the
  launch-gate governs it (processes/launch-gate.md). Default bind is loopback.
"""
import http.cookies
import http.server
import json
import os
import re
import socketserver
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CONSOLE = os.path.join(REPO, "processes", "partnerships", "connector-console")
sys.path.insert(0, CONSOLE)
import auth  # noqa: E402  — the single auth authority; its store lives beside it

HOST = os.environ.get("YOURCO_APP_HOST", "127.0.0.1")

def _port(launch_name, fallback):
    """Backend ports come from .claude/launch.json, which is the registry of every local surface and
    is already invariant-checked for duplicates. Hardcoding them here would be a second copy of a fact
    that lives somewhere else — the exact duplication removed from show.sh earlier the same day and
    then reintroduced here hours later, which is how well duplication hides.

    The fallback exists so the gateway still starts if the registry is unreadable; it is a last resort,
    not a default, and it says so if it fires.
    """
    try:
        with open(os.path.join(REPO, ".claude", "launch.json"), encoding="utf-8") as fh:
            for c in json.load(fh)["configurations"]:
                if c.get("name") == launch_name:
                    return int(c["port"])
    except Exception as e:
        sys.stderr.write(f"  ⚠ could not read {launch_name} from launch.json ({e}); "
                         f"falling back to :{fallback}\n")
    else:
        sys.stderr.write(f"  ⚠ '{launch_name}' is not in .claude/launch.json; "
                         f"falling back to :{fallback}\n")
    return fallback


PORT = int(os.environ.get("YOURCO_APP_PORT") or 0) or _port("yourco-app", 8820)

# area -> (url prefix, backend origin, needs-this-permission)
AREAS = {
    "hq":        ("/hq",        os.environ.get("YOURCO_HQ_URL") or f"http://127.0.0.1:{_port('yourco-hq', 8791)}", "hq"),
    "crm":       ("/crm",       os.environ.get("YOURCO_CRM_URL") or f"http://127.0.0.1:{_port('yourco-crm', 8790)}", "crm"),
    "connector": ("/connector", os.environ.get("YOURCO_CONSOLE_URL") or f"http://127.0.0.1:{_port('yourco-connector-console', 8807)}", "console"),
}
NAV = [("hq", "HQ", "The company dashboard"),
       ("crm", "CRM", "Pipeline and contacts"),
       ("connector", "Connectors", "The connector program")]

HOP_BY_HOP = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
              "te", "trailers", "transfer-encoding", "upgrade", "content-encoding",
              "content-length", "host"}


def shim(prefix):
    """Make an app mounted at /<prefix> behave as if it were at the root.

    Both UIs call fetch('/api/...') with an absolute path. Under a prefix that resolves to
    the gateway root and 404s. Rather than edit 7,500 lines, wrap fetch once.
    """
    return (
        "<script>(function(){var P=%s;"
        "var f=window.fetch;window.fetch=function(u,o){"
        "if(typeof u==='string'&&u.charAt(0)==='/'&&u.indexOf(P+'/')!==0){u=P+u;}"
        "return f.call(this,u,o);};"
        "})();</script>" % json.dumps(prefix)
    )


def switcher(role, current):
    """A way out of a mounted app that does not depend on the browser's back button.

    Without this the only route from HQ back to the CRM is Back — and in an installed PWA
    running standalone there is often no back button at all, which makes the app a one-way door.

    Placement was measured, not guessed. A fixed TOP bar was the first instinct and is wrong:
    HQ's sidebar is position:sticky/top:0, so it would slide underneath. Bottom-LEFT was the
    second and is also wrong: it lands on HQ's own avatar block. HQ's Melanie orb sits at
    right:24px/bottom:24px, so bottom-right offset past it is the one corner free in all three
    apps. On narrow screens it stacks above the orb instead, where there is no room beside it.

    Rendered server-side from the session's role, so an area the role cannot reach is not in
    the DOM at all — the switcher can never offer a door that 403s.
    """
    items = []
    for area, label, _blurb in NAV:
        pre, _o, perm = AREAS[area]
        if not auth.can_access(role, perm):
            continue
        here = " ia-on" if area == current else ""
        items.append(f'<a class="ia-i{here}" href="{pre}/">{esc(label)}</a>')
    items.append('<a class="ia-i ia-out" href="/logout">Sign out</a>')
    links = "".join(items)
    return f"""<style>
#ia-sw{{position:fixed;right:96px;bottom:20px;z-index:9000;font:500 13px/1.2 -apple-system,system-ui,Inter,sans-serif}}
#ia-sw *{{box-sizing:border-box}}
#ia-b{{display:flex;align-items:center;gap:7px;background:#1c2240;color:#F4EFE6;border:1px solid rgba(244,239,230,.22);
 border-radius:999px;padding:11px 15px;cursor:pointer;box-shadow:0 6px 22px rgba(0,0,0,.4)}}
#ia-b:hover{{border-color:#B8965A}}
#ia-b .d{{width:7px;height:7px;border-radius:50%;background:#B8965A;flex:none}}
#ia-m{{display:none;position:absolute;right:0;bottom:calc(100% + 9px);min-width:196px;background:#1c2240;
 border:1px solid rgba(244,239,230,.22);border-radius:13px;padding:6px;box-shadow:0 10px 34px rgba(0,0,0,.5)}}
#ia-sw.open #ia-m{{display:block}}
.ia-i{{display:block;padding:11px 13px;border-radius:9px;color:#F4EFE6;text-decoration:none;white-space:nowrap}}
.ia-i:hover{{background:rgba(244,239,230,.09)}}
.ia-on{{color:#B8965A}}
.ia-on::after{{content:" ·  here";font-size:11px;opacity:.6}}
.ia-out{{border-top:1px solid rgba(244,239,230,.14);margin-top:5px;padding-top:11px;color:rgba(244,239,230,.66)}}
@media(max-width:600px){{#ia-sw{{right:14px;bottom:calc(88px + env(safe-area-inset-bottom))}}}}
@media print{{#ia-sw{{display:none}}}}
</style>
<div id="ia-sw"><div id="ia-m">{links}</div>
<div id="ia-b" role="button" tabindex="0" aria-haspopup="true" aria-expanded="false"><span class="d"></span>yourco</div></div>
<script>(function(){{var w=document.getElementById('ia-sw'),b=document.getElementById('ia-b');
function t(e){{e.preventDefault();e.stopPropagation();var o=w.classList.toggle('open');b.setAttribute('aria-expanded',o);}}
b.addEventListener('click',t);
b.addEventListener('keydown',function(e){{if(e.key==='Enter'||e.key===' ')t(e);}});
document.addEventListener('click',function(e){{if(!w.contains(e.target))w.classList.remove('open');}});
document.addEventListener('keydown',function(e){{if(e.key==='Escape')w.classList.remove('open');}});
}})();</script>"""


def rewrite_html(body, prefix, role=None, area=None):
    """Prefix the absolute links an app emits, and inject the fetch shim.

    Deliberately narrow: only href/action attributes that start with a single slash, and
    only in HTML. Protocol-relative (//host) and absolute URLs are left alone, which is why
    the pattern requires a non-slash next character.
    """
    text = body.decode("utf-8", "replace")
    text = re.sub(r'(href|action)="/(?!/)', r'\1="%s/' % prefix, text)
    if "</head>" in text:
        text = text.replace("</head>", shim(prefix) + "</head>", 1)
    else:
        text = shim(prefix) + text
    # The switcher goes at the END of body: it is fixed-position so placement does not affect
    # layout, and appending means it cannot land inside an app's own container and inherit
    # styles from it.
    if role:
        sw = switcher(role, area)
        text = text.replace("</body>", sw + "</body>", 1) if "</body>" in text else text + sw
    return text.encode("utf-8")


class Gateway(http.server.BaseHTTPRequestHandler):
    server_version = "yourco-app"

    # ── plumbing ────────────────────────────────────────────────────────────
    def log_message(self, fmt, *a):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % a))

    def _send(self, code, body, ctype="text/html; charset=utf-8", extra=()):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        # These three cost nothing and close the obvious classes of mistake.
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        for k, v in extra:
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _redirect(self, to, extra=()):
        self._send(303, b"", extra=tuple(extra) + (("Location", to),))

    def _session(self):
        raw = self.headers.get("Cookie")
        return auth.session_for(auth.cookie_from_header(raw)) if raw else None

    # ── the proxy ───────────────────────────────────────────────────────────
    def _proxy(self, area, rest, body=None, role=None):
        prefix, origin, _perm = AREAS[area]
        url = origin + (rest or "/")
        req = urllib.request.Request(url, data=body, method=self.command)
        for k, v in self.headers.items():
            lk = k.lower()
            if lk in HOP_BY_HOP:
                continue
            # Origin/Referer must describe the backend, not the gateway. HQ CSRF-checks POSTs by
            # comparing Origin's netloc to Host; Host is hop-by-hop so urllib rewrites it to the
            # backend, and the browser's Origin still said :8820 — so every HQ write 403'd. The
            # gateway is the security boundary (it authenticated and role-checked before we got
            # here), so presenting a coherent same-origin view to the backend is correct, not a
            # bypass: the backend is unreachable from anywhere else.
            if lk in ("origin", "referer"):
                v = origin if lk == "origin" else origin + rest
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                payload, status, headers = r.read(), r.status, dict(r.headers)
        except urllib.error.HTTPError as e:          # 4xx/5xx are real answers — pass them on
            payload, status, headers = e.read(), e.code, dict(e.headers)
        except urllib.error.URLError as e:
            # A backend being down must read as a backend being down, not as a broken app.
            return self._send(502, f"<h1>{area} is not running</h1><p>The gateway is up but "
                                   f"<code>{origin}</code> did not answer ({e.reason}). "
                                   f"Start it with <code>./show.sh</code>.</p>")
        # HTTP header names are case-insensitive, and dict(r.headers) is not. The backends use
        # Python's stdlib default, which emits "Content-type" with a lowercase t — so a
        # headers.get("Content-Type") lookup silently returned nothing, the HTML never matched
        # the text/html test, and the fetch shim was never injected. Found by testing the
        # proxied page rather than the proxied API: the API worked, the UI would not have.
        ctype = next((v for k, v in headers.items() if k.lower() == "content-type"), "")
        if "text/html" in ctype:
            payload = rewrite_html(payload, prefix, role=role, area=area)
        out = [(k, v) for k, v in headers.items()
               if k.lower() not in HOP_BY_HOP and k.lower() != "content-type"]
        # A backend redirecting to /x must land inside its own mount, not at the gateway root.
        out = [(k, (prefix + v if k.lower() == "location" and v.startswith("/")
                    and not v.startswith(prefix) else v)) for k, v in out]
        self._send(status, payload, ctype or "application/octet-stream", tuple(out))

    # ── routing ─────────────────────────────────────────────────────────────
    def _same_origin(self):
        """Reject a cross-origin state-changing request before it reaches a backend.

        This exists because the proxy REWRITES Origin to match the backend it forwards to — HQ
        CSRF-checks POSTs by comparing Origin's netloc to Host, and without the rewrite every HQ
        write 403'd through the gateway. But rewriting means HQ's own check can no longer fail,
        so the gateway silently became the only thing standing between a cross-site POST and a
        backend write. The first version shipped without this and the commit described it as
        "correct, not a bypass". It was a bypass.

        What actually prevented exploitation was `SameSite=Strict` on the session cookie (set in
        auth.py) — a cross-site request never carries the cookie and dies at the login redirect.
        That is a real control, but it lives in another module and was not verified when the
        rewrite was written. One unverified control is not a security posture.

        Same-origin form posts often omit Origin entirely, so absence is allowed — the same
        judgement the console makes.
        """
        origin = self.headers.get("Origin")
        if not origin:
            return True
        host = self.headers.get("Host", "")
        return urllib.parse.urlparse(origin).netloc == host

    def _route(self, body=None):
        path = urllib.parse.urlparse(self.path).path
        full = self.path

        # Every state-changing request, before auth and before any proxying.
        if self.command == "POST" and not self._same_origin():
            return self._send(403, "<h1>Cross-origin request refused</h1>"
                                   "<p>This request did not come from the app.</p>",
                              "text/html; charset=utf-8")

        if path == "/healthz":                       # no auth: for uptime checks only
            return self._send(200, "ok", "text/plain; charset=utf-8")
        if path in ("/manifest.webmanifest", "/manifest.json"):
            return self._send(200, read("manifest.webmanifest"), "application/manifest+json")
        if path == "/sw.js":
            return self._send(200, read("sw.js"), "application/javascript; charset=utf-8")
        if path == "/app.css":
            return self._send(200, read("app.css"), "text/css; charset=utf-8")
        if path == "/icon.svg":
            return self._send(200, read("icon.svg"), "image/svg+xml")

        if path == "/login":
            if self.command == "POST":
                return self._post_login(body)
            return self._send(200, login_page())
        if path == "/logout":
            s = self._session()
            if s:
                auth.destroy_session(auth.cookie_from_header(self.headers.get("Cookie") or ""))
            return self._redirect("/login",
                                  (("Set-Cookie", auth.clear_cookie(self.headers.get("Host"))),))

        who = self._session()
        if not who:
            return self._redirect("/login")

        if path == "/":
            return self._send(200, shell_page(who))

        for area, (prefix, _origin, perm) in AREAS.items():
            if path == prefix or path.startswith(prefix + "/"):
                if not auth.can_access(who.get("role"), perm):
                    # Say what happened. A silent redirect to the shell reads as a broken link.
                    return self._send(403, denied_page(who, area))
                rest = full[len(prefix):] or "/"
                return self._proxy(area, rest, body, role=who.get("role"))

        return self._send(404, "<h1>Not found</h1><p><a href=\"/\">Back to yourco</a></p>")

    def do_GET(self):
        self._route()

    def do_HEAD(self):
        self._route()

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        self._route(self.rfile.read(n) if n else b"")

    def _post_login(self, body):
        form = urllib.parse.parse_qs((body or b"").decode("utf-8", "replace"))
        name = (form.get("name") or [""])[0].strip()
        pw = (form.get("passphrase") or [""])[0]
        ip = self.client_address[0] if self.client_address else None
        if auth.ip_blocked(ip):
            return self._send(429, login_page("Too many attempts. Wait a few minutes."))
        ok, user, msg = auth.verify(name, pw, ip=ip)
        if not ok:
            return self._send(401, login_page(msg or auth.FAIL_MSG))
        sid, _csrf = auth.create_session(user["name"], user["role"])
        return self._redirect("/", (("Set-Cookie",
                                     auth.set_cookie(sid, self.headers.get("Host"))),))


def read(name):
    with open(os.path.join(HERE, name), "rb") as f:
        return f.read()


# ── pages ───────────────────────────────────────────────────────────────────
def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def page(title, inner, cls=""):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#161B33">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>{esc(title)}</title>
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/icon.svg">
<link rel="stylesheet" href="/app.css">
</head><body class="{cls}">{inner}
<script>if('serviceWorker' in navigator)navigator.serviceWorker.register('/sw.js');</script>
</body></html>"""


def login_page(msg=""):
    err = f'<p class="err">{esc(msg)}</p>' if msg else ""
    return page("Sign in — yourco", f"""
<main class="auth">
  <div class="mark">yourco<span>.</span></div>
  <p class="sub">Sign in to the OS</p>
  {err}
  <form method="POST" action="/login">
    <label>Name<input name="name" autocomplete="username" autocapitalize="words" required autofocus></label>
    <label>Passphrase<input name="passphrase" type="password" autocomplete="current-password" required></label>
    <button type="submit">Sign in</button>
  </form>
  <p class="fine">Access is per-person and role-scoped. Sessions expire on idle.</p>
</main>""", "is-auth")


def denied_page(who, area):
    return page("Not your area — yourco", f"""
<main class="auth">
  <div class="mark">yourco<span>.</span></div>
  <p class="sub">{esc(area.upper())} is not open to your role</p>
  <p class="fine">You are signed in as <b>{esc(who.get('name'))}</b> ({esc(who.get('role'))}).
     That role can reach: {esc(', '.join(sorted(auth.areas_for(who.get('role')))) or 'nothing')}.</p>
  <p><a class="btn" href="/">Back to yourco</a></p>
</main>""", "is-auth")


def shell_page(who):
    role = who.get("role") or ""
    cards = []
    for area, label, blurb in NAV:
        _p, _o, perm = AREAS[area]
        if not auth.can_access(role, perm):
            continue
        cards.append(f'<a class="card" href="{AREAS[area][0]}/">'
                     f'<span class="k">{esc(label)}</span>'
                     f'<span class="b">{esc(blurb)}</span></a>')
    if not cards:
        cards.append('<p class="fine">Your role has no areas assigned. Ask the Founder.</p>')
    shown = "partner" if role == "operator" else role
    return page("yourco", f"""
<header class="top">
  <span class="mark">yourco<span>.</span></span>
  <span class="who">{esc(who.get('name'))} · {esc(shown)}</span>
  <a class="out" href="/logout">Sign out</a>
</header>
<main class="grid">{''.join(cards)}</main>
<footer class="fine">Everything here is internal. Nothing on this device is client-facing.</footer>""")


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    if HOST not in ("127.0.0.1", "localhost", "::1"):
        # Loud on purpose. Public exposure is an launch-gate decision, not a flag someone flips.
        sys.stderr.write(
            f"\n  ⚠️  BINDING TO {HOST} — this is NOT loopback.\n"
            "     HQ and the CRM have no authentication of their own; this gateway is the only\n"
            "     thing standing in front of them. Public exposure is governed by the OtherVenture\n"
            "     gate (processes/launch-gate.md). Confirm that has cleared.\n\n")
    print(f"yourco app gateway → http://{HOST}:{PORT}/  (login required)")
    for a, (p, o, perm) in AREAS.items():
        print(f"    {p:<11} → {o:<24} requires: {perm}")
    Server((HOST, PORT), Gateway).serve_forever()
