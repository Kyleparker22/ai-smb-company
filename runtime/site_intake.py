#!/usr/bin/env python3
"""yourco — site form intake: the launch-gated backend for the website's two staged forms.

The staged site already POSTs (fire-and-forget) to relative endpoints:
  • audit-intake.html → POST /api/audit-intake   (the paid-audit request — the site's primary CTA)
  • careers.html      → POST /api/rep-intake     (referral-partner application)

This handler makes those real:
  audit-intake → CRM warm lead (company + contact + prospect deal + activity; owner Bella,
                 source "audit intake form"; dedupe by email/company) + Slack #yourco-bella.
  rep-intake   → CRM contact (kind internal/connector; status "connector applicant", owner Bird) + activity
                 + Slack #yourco-bird. NO terms are sent automatically — the program is
                 counsel-gated; a human follows up with the packet.

Conventions mirror runtime/snapshot_intake.py + runtime/promote.py. CRM writes go through the
cross-process lock (dashboard/melanie.crm_lock) when importable — never a bare overwrite.

STAGED: nothing serves until launch. At launch: run --serve behind the site host's reverse proxy
(systemd unit: runtime/systemd/yourco-site-intake.service — register it in agent-registry.json
sanctioned_daemons_no_timer THE SAME DAY it's enabled, or the governance watchdog will flag it).

Usage:
  python3 runtime/site_intake.py --self-check            # dry-run both sample payloads
  python3 runtime/site_intake.py --self-check --commit   # write the samples into the CRM
  python3 runtime/site_intake.py --serve [port]          # launch-gated HTTP mode (default 8797)
"""
import json, os, re, sys, datetime, urllib.request, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def _today():
    """Creation date for a new company. `createdAtSource` distinguishes this from the dates
    recovered out of git for the 25 companies that predate the field (2026-08-13) — a recovered
    date and an observed one must never read the same."""
    import datetime as _dt
    return _dt.date.today().isoformat()


HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CRM = os.path.join(REPO, "crm", "data.json")
sys.path.insert(0, os.path.join(REPO, "dashboard"))

AUDIT_OWNER, REP_OWNER = "Bella", "Bird"
AUDIT_CHANNEL, REP_CHANNEL = "#yourco-bella", "#yourco-bird"
MAXLEN = 4000  # crude input bound per field


def _slack_env():
    p = os.path.join(HERE, ".slack.env")
    env = {}
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def post_slack(channel, text):
    bot = os.environ.get("SLACK_BOT_TOKEN") or _slack_env().get("SLACK_BOT_TOKEN")
    if not bot:
        print("(no SLACK_BOT_TOKEN — skipping Slack post)")
        return False
    data = urllib.parse.urlencode({"channel": channel, "text": text,
                                   "unfurl_links": "false", "unfurl_media": "false"}).encode()
    req = urllib.request.Request("https://slack.com/api/chat.postMessage", data=data,
                                 headers={"Authorization": f"Bearer {bot}"})
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
        return bool(resp.get("ok"))
    except Exception as e:
        print("Slack post failed:", e)
        return False


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _next_id(prefix, items):
    mx = 0
    for it in items:
        m = re.match(rf"{prefix}(\d+)$", str(it.get("id", "")))
        if m: mx = max(mx, int(m.group(1)))
    return f"{prefix}{mx+1}"


def _clean(p):
    return {k: str(v)[:MAXLEN] for k, v in (p or {}).items() if isinstance(k, str)}


def _load_crm():
    return json.load(open(CRM))


def _save_crm(crm):
    crm.setdefault("meta", {})["updated"] = datetime.date.today().isoformat()
    try:
        import melanie  # the locked, atomic path (three writers share this file)
        with melanie.crm_lock():
            melanie._atomic_dump(CRM, crm)
            melanie.write_mirror(crm)
        return
    except Exception:
        tmp = f"{CRM}.tmp.{os.getpid()}"
        json.dump(crm, open(tmp, "w"), indent=1, ensure_ascii=False)
        os.replace(tmp, CRM)


def handle_audit(p, commit=False):
    """Audit-intake form → warm lead. Highest-intent inbound on the site."""
    p = _clean(p)
    today = datetime.date.today().isoformat()
    crm = _load_crm()
    companies, contacts = crm.setdefault("companies", []), crm.setdefault("contacts", [])
    deals, acts = crm.setdefault("deals", []), crm.setdefault("activities", [])
    email = (p.get("email") or "").strip().lower()
    cname = p.get("company") or p.get("business") or p.get("name") or ""
    dup = (email and any((c.get("email") or "").lower() == email for c in contacts)) or \
          (cname and any(_norm(c.get("name")) == _norm(cname) for c in companies))
    summary = (f"Audit request from the site. Revenue: {p.get('revenue','—')} · "
               f"team: {p.get('team','—')} · pain: {p.get('pain') or p.get('bottleneck') or '—'}")
    slack = (f":rotating_light: *Audit request — {cname or p.get('name','?')}*\n"
             f"{p.get('name','')} · {p.get('email','')} · {p.get('phone','') or '—'}\n{summary}\n"
             f"_{'Already in the CRM — activity logged.' if dup else f'In the CRM as a warm lead, owner {AUDIT_OWNER}.'}"
             f" Next: book the audit call._")
    out = {"ok": True, "duplicate": dup, "slack": slack, "crm_written": False}
    if not commit:
        out["action"] = "dry-run"
        return out
    if dup:
        match = next((co for co in companies if _norm(co.get("name")) == _norm(cname)), None)
        acts.append({"date": today, "type": "audit-request", "companyId": match["id"] if match else None,
                     "who": p.get("name", ""), "summary": summary, "nextAction": "Book the audit call"})
    else:
        cid = _next_id("c", companies)
        companies.append({"id": cid, "name": cname or "(unknown)", "vertical": p.get("industry", ""),
                          "size": p.get("team", ""), "location": "", "source": "audit intake form",
                          "channel": "inbound-site", "channelSource": "recorded",
                          "status": "prospect", "owner": AUDIT_OWNER, "domain": "",
                          "example": False,
                          "createdAt": _today(), "createdAtSource": "recorded"})
        contacts.append({"id": _next_id("p", contacts), "name": p.get("name", ""), "companyId": cid,
                         "role": "Owner", "relationship": "requested the audit via the site",
                         "email": p.get("email", ""), "phone": p.get("phone", ""),
                         "lastTouch": today, "status": "warm — audit request", "example": False})
        deals.append({"id": _next_id("d", deals), "name": f"{cname or p.get('name','')} — audit",
                      "companyId": cid, "useCase": p.get("pain") or "TBD — scope in the audit",
                      # `prospect` was retired in the 2026-08-07 ladder restructure — the AUDIT
                      # intake form, the front door of the entire motion, was creating every lead
                      # on a rung that no longer exists. Caught by the intake-writer invariant
                      # 2026-08-25, not by eye.
                      "stage": "pre-convo", "buildFee": None, "retainer": None, "value": 0,
                      "nextAction": "Book the audit call", "nextDate": "", "lastTouch": today,
                      "owner": AUDIT_OWNER, "stageSince": today, "example": False,
                      "stageHistory": [{"stage": "pre-convo", "at": today, "source": "recorded"}]})
        acts.append({"date": today, "type": "Audit requested", "companyId": cid,
                     "who": p.get("name", ""), "summary": summary, "nextAction": "Book the audit call"})
    _save_crm(crm)
    out.update(action="written", crm_written=True)
    post_slack(AUDIT_CHANNEL, slack)
    return out


def handle_rep(p, commit=False):
    """Careers/rep form → applicant contact + activity. Human follows up (program counsel-gated)."""
    p = _clean(p)
    today = datetime.date.today().isoformat()
    crm = _load_crm()
    contacts, acts = crm.setdefault("contacts", []), crm.setdefault("activities", [])
    email = (p.get("email") or "").strip().lower()
    dup = email and any((c.get("email") or "").lower() == email for c in contacts)
    pitch = (p.get("pitch") or "")[:600]
    slack = (f":handshake: *Connector application*\n"
             f"{p.get('name','?')} · {p.get('email','')} · {p.get('phone','') or '—'}\n"
             f"Network: {pitch or '—'}\n"
             f"_Owner {REP_OWNER}. Next: human review → send the Connector Packet. (Program is counsel-gated — no terms sent automatically.)_")
    out = {"ok": True, "duplicate": bool(dup), "slack": slack, "crm_written": False}
    if not commit:
        out["action"] = "dry-run"
        return out
    if not dup:
        contacts.append({"id": _next_id("p", contacts), "name": p.get("name", ""), "companyId": None,
                         "role": None, "kind": "internal", "teamRole": "connector", "teamStatus": "prospect",
                         "relationship": "applied via careers page",
                         "email": p.get("email", ""), "phone": p.get("phone", ""),
                         "lastTouch": today, "status": "connector applicant", "example": False,
                         "notes": pitch})
    acts.append({"date": today, "type": "rep-application", "companyId": None,
                 "who": p.get("name", ""), "summary": f"Referral-partner application. {pitch[:200]}",
                 "nextAction": "Review + send the Connector Packet (post-counsel)"})
    _save_crm(crm)
    out.update(action="written", crm_written=True)
    post_slack(REP_CHANNEL, slack)
    return out


ROUTES = {"/api/audit-intake": handle_audit, "/api/rep-intake": handle_rep}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        fn = ROUTES.get(self.path)
        if not fn:
            return self._json(404, {"error": "unknown endpoint"})
        try:
            n = min(int(self.headers.get("Content-Length", 0)), 64_000)
            p = json.loads(self.rfile.read(n).decode() or "{}")
        except Exception:
            return self._json(400, {"error": "bad payload"})
        try:
            out = fn(p, commit=True)
            return self._json(200, {"ok": True, "duplicate": out.get("duplicate", False)})
        except Exception as e:
            print("intake error:", e)
            return self._json(500, {"error": "intake failed"})


_SAMPLES = {
    "audit": {"name": "Sample Owner", "email": "sample.audit@example.com", "company": "Sample Services (TEST)",
              "phone": "(555) 010-0102", "industry": "Plumbing", "revenue": "$40k/mo", "team": "6",
              "pain": "missed calls + quotes take nights"},
    "rep": {"name": "Sample Rep", "email": "sample.rep@example.com", "phone": "(555) 010-0103",
            "pitch": "I run a bookkeeping practice with ~40 small-business clients across the trades."},
}

if __name__ == "__main__":
    if "--serve" in sys.argv:
        port = int(sys.argv[sys.argv.index("--serve") + 1]) if len(sys.argv) > sys.argv.index("--serve") + 1 and sys.argv[sys.argv.index("--serve") + 1].isdigit() else 8797
        host = os.environ.get("INTAKE_HOST", "127.0.0.1")
        print(f"site-intake serving on {host}:{port} (launch-gated — put behind the site's reverse proxy)")
        ThreadingHTTPServer((host, port), H).serve_forever()
    else:
        commit = "--commit" in sys.argv
        print("== audit-intake sample ==")
        print(json.dumps(handle_audit(_SAMPLES["audit"], commit=commit), indent=2)[:600])
        print("== rep-intake sample ==")
        print(json.dumps(handle_rep(_SAMPLES["rep"], commit=commit), indent=2)[:600])
        print("self-check done (commit=%s)" % commit)
