#!/usr/bin/env python3
"""Instantly -> CRM sync (David's integration).

Pulls Reilly's Instantly campaign results into the CRM (the source of truth):
  - campaign-level analytics  -> a sync summary
  - interested + replied leads -> upserted as company / contact / deal / activity

READ-ONLY against Instantly. This NEVER sends, creates, or modifies anything in
Instantly — sending stays Reilly's job and is launch-gated (CAN-SPAM/warmup).
Writes only to our own CRM (crm/data.json + the data.js mirror). Idempotent:
re-running matches companies by name and contacts by email, so no duplicates.

Credentials (create once, never paste into chat):
  Instantly -> Settings -> API keys -> create a key.
  Scope: `all:read` is sufficient — this script is READ-ONLY (campaigns, analytics, and the
  read-only POST /api/v2/leads/list endpoint). It never creates, sends, or modifies anything
  in Instantly. (Note: POST /api/v2/leads — without /list — is the *create* endpoint; we
  deliberately use /list, which is a read.)
  Save to ~/.yourco/instantly.env (gitignored):
      INSTANTLY_API_KEY=your_key

Run:  python3 crm/integrations/instantly_sync.py
Pre-launch (no campaigns yet) it will simply report "connection verified, nothing to sync."
"""
import os, sys, json, time, datetime, urllib.request, urllib.parse, urllib.error

def _today():
    """Creation date for a new company. `createdAtSource` distinguishes this from the dates
    recovered out of git for the 25 companies that predate the field (2026-08-13) — a recovered
    date and an observed one must never read the same."""
    import datetime as _dt
    return _dt.date.today().isoformat()


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_JSON = os.path.join(ROOT, "crm", "data.json")
DATA_JS = os.path.join(ROOT, "crm", "data.js")
ENV_FILE = os.path.expanduser("~/.yourco/instantly.env")
BASE = "https://api.instantly.ai"
TODAY = datetime.date.today().isoformat()

# Instantly enums -> our CRM
INTEREST = {1: "Interested", 2: "Meeting booked", 3: "Meeting completed", 4: "Won",
            -1: "Not interested", -2: "Wrong person", -3: "Lost", -4: "No show", 0: "Out of office"}
def stage_for(interest):
    if interest in (1, 2, 3):
        return "discovery"
    if interest == 4:
        return "proposal"
    return "prospect"  # replied but no interest set yet


def load_key():
    if os.path.exists(ENV_FILE):
        for line in open(ENV_FILE):
            line = line.strip()
            if line.startswith("INSTANTLY_API_KEY="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("INSTANTLY_API_KEY")


def api(method, path, key, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json",
                                          "Accept": "application/json",
                                          "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                                                         "Chrome/124.0.0.0 Safari/537.36")})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(f"  ! {method} {path} -> HTTP {e.code}: {e.read().decode()[:200]}", file=sys.stderr)
        raise


def get_analytics(key):
    try:
        res = api("GET", "/api/v2/campaigns/analytics", key)
        return res if isinstance(res, list) else res.get("items", res) or []
    except Exception:
        return []


def get_leads(key, filt):
    """Page through leads matching a single filter (e.g. FILTER_LEAD_INTERESTED)."""
    out, after = [], None
    while True:
        body = {"filter": filt, "limit": 100}
        if after:
            body["starting_after"] = after
        res = api("POST", "/api/v2/leads/list", key, body)
        items = res.get("items", [])
        out.extend(items)
        after = res.get("next_starting_after")
        if not after or not items:
            break
        time.sleep(0.3)
    return out


def load_crm():
    return json.load(open(DATA_JSON))


def save_crm(db):
    json.dump(db, open(DATA_JSON, "w"), indent=2, ensure_ascii=False)
    with open(DATA_JS, "w") as f:
        f.write("/* AUTO-GENERATED from data.json by server.py. Source of truth is data.json. */\n")
        f.write("window.CRM_DATA = " + json.dumps(db, indent=2, ensure_ascii=False) + ";\n")


def next_id(items, prefix):
    n = 0
    for it in items:
        v = str(it.get("id", ""))
        if v.startswith(prefix) and v[len(prefix):].isdigit():
            n = max(n, int(v[len(prefix):]))
    return f"{prefix}{n + 1}"


def upsert(db, lead):
    """Upsert one Instantly lead into the CRM. Returns a one-line note of what changed."""
    email = (lead.get("email") or "").lower().strip()
    if not email:
        return None
    cname = (lead.get("company_name") or "").strip() or (email.split("@")[1] if "@" in email else "Unknown")
    interest = lead.get("lt_interest_status")
    interest_label = INTEREST.get(interest, "Replied")
    fullname = " ".join(x for x in [lead.get("first_name"), lead.get("last_name")] if x).strip() or email

    # Company (match by name, case-insensitive)
    company = next((c for c in db["companies"] if c["name"].lower() == cname.lower()), None)
    if not company:
        company = {"id": next_id(db["companies"], "c"), "name": cname, "vertical": "",
                   "size": "", "location": "", "source": "Reilly / Instantly",
                   "status": stage_for(interest), "owner": "Reilly",
                   "createdAt": _today(), "createdAtSource": "recorded"}
        db["companies"].append(company)
        action = "new company"
    else:
        action = "updated"

    # Contact (match by email)
    contact = next((p for p in db["contacts"] if (p.get("email") or "").lower() == email), None)
    if not contact:
        contact = {"id": next_id(db["contacts"], "p"), "name": fullname, "companyId": company["id"],
                   "role": "", "email": email, "phone": lead.get("phone") or "",
                   "lastTouch": TODAY, "status": interest_label}
        db["contacts"].append(contact)
    else:
        contact["lastTouch"] = TODAY
        contact["status"] = interest_label

    # Deal (one per company; create if none)
    deal = next((d for d in db["deals"] if d.get("companyId") == company["id"]), None)
    if not deal:
        deal = {"id": next_id(db["deals"], "d"), "name": f"{cname} — intake employee",
                "companyId": company["id"], "useCase": "Inbound intake (from outreach reply)",
                "stage": stage_for(interest), "buildFee": None, "retainer": None, "value": 0,
                "nextAction": "Qualify the reply / book discovery", "nextDate": TODAY,
                "lastTouch": TODAY, "owner": "Reilly"}
        db["deals"].append(deal)
    else:
        deal["lastTouch"] = TODAY
        # only advance stage forward, never backward
        order = ["prospect", "discovery", "proposal", "build", "live"]
        new = stage_for(interest)
        if order.index(new) > order.index(deal.get("stage", "prospect")):
            deal["stage"] = new

    # Activity
    db["activities"].insert(0, {"date": TODAY, "type": "reply", "companyId": company["id"],
                                "who": fullname, "summary": f"Instantly: {interest_label}.",
                                "nextAction": "Reilly/the Founder qualify"})
    return f"{cname} <{email}> — {interest_label} ({action})"


def main():
    key = load_key()
    if not key:
        print(f"No Instantly API key. Create one in Instantly -> Settings -> API keys,\n"
              f"then save to {ENV_FILE}:\n  INSTANTLY_API_KEY=...")
        sys.exit(1)

    print("Connecting to Instantly…")
    analytics = get_analytics(key)
    try:
        interested = get_leads(key, "FILTER_LEAD_INTERESTED")
        replied = get_leads(key, "FILTER_VAL_REPLIED")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("\n⚠ Lead sync skipped — the API key lacks read access to leads.\n"
                  "  Ensure the key has `all:read` (or `leads:read`). Campaign analytics still synced.\n")
            interested, replied = [], []
        else:
            raise
    # dedupe by id, interested wins
    leads = {l.get("id"): l for l in replied}
    leads.update({l.get("id"): l for l in interested})
    leads = [l for l in leads.values() if l.get("email")]

    db = load_crm()
    notes = [n for n in (upsert(db, l) for l in leads) if n]
    if notes:
        save_crm(db)

    # Summary artifact
    date = TODAY
    out = [f"# Instantly → CRM sync — {date}", "",
           f"Campaigns: {len(analytics)} · interested leads: {len(interested)} · replied leads: {len(replied)}",
           f"Synced into CRM: {len(notes)} lead(s).", ""]
    if analytics:
        out.append("## Campaign analytics")
        for a in analytics:
            out.append(f"- **{a.get('campaign_name','?')}** — sent {a.get('emails_sent_count',0)}, "
                       f"opens {a.get('open_count',0)}, replies {a.get('reply_count',0)}, "
                       f"bounced {a.get('bounced_count',0)}, opportunities {a.get('total_opportunities',0)}")
        out.append("")
    if notes:
        out.append("## Leads synced to CRM")
        out += [f"- {n}" for n in notes]
    else:
        out.append("_No interested/replied leads to sync yet — connection verified._")
    log = os.path.join(ROOT, "crm", "integrations", "instantly-last-sync.md")
    open(log, "w").write("\n".join(out) + "\n")
    print("\n".join(out))
    print(f"\n→ wrote {log}")
    if notes:
        print(f"→ updated {DATA_JSON} (+ data.js mirror)")


if __name__ == "__main__":
    main()
