#!/usr/bin/env python3
"""yourco — Sadie intent signals → the CRM Hot List, two lanes with very different gates.

Lane 1 — ATTACH (safe, automatic): a signal that matches a company ALREADY in the CRM is appended to
that company's `signals[]` array (the Hot List renders these as pills and scores their heat). Pure
enrichment of existing records — no rows are ever created — so the sweep loop calls it after each run.
De-duped by signal URL; a signal attaches once, ever.

Lane 2 — PROMOTE (gated, human-triggered): an unmatched prospect-grade signal enters the CRM only
after a human identifies the real business behind the handle. Mirrors runtime/promote.py (the
Instantly gate): company + contact + prospect-stage deal owned by Reilly, the signal attached as the
first Hot List pill. Dry-run by default; --commit writes. This is the ONLY path a Sadie signal
becomes a CRM row (skill: .claude/skills/promote-intent-signal/).

Why no auto-create: Sadie's signals are mostly anonymous social handles, and the scorer still passes
the odd vendor ad (the Zebra Go misclass, first live sweep 2026-07-20). Ghost rows rot the fit-score
math; identification stays human until Kolby's precision eval earns it up the autonomy matrix.

Usage:
  python3 runtime/promote_intent.py --attach                # dry-run lane 1 over recent boards
  python3 runtime/promote_intent.py --attach --commit       # write matched signals into crm/data.json
  python3 runtime/promote_intent.py --list                  # unmatched prospect-grade signals (promotion candidates)
  python3 runtime/promote_intent.py --promote --signal-url URL --company "YourCo Hardscapes" \
      --vertical Hardscaping [--domain yourco.com] [--location "Yourtown"] \
      [--contact "Joe Smith"] [--email joe@yourco.com] [--commit]
"""
import os, sys, json, re, glob, datetime

def _today():
    """Creation date for a new company. `createdAtSource` distinguishes this from the dates
    recovered out of git for the 25 companies that predate the field (2026-08-13) — a recovered
    date and an observed one must never read the same."""
    import datetime as _dt
    return _dt.date.today().isoformat()


HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CRM = os.path.join(REPO, "crm", "data.json")
BOARDS = os.path.join(REPO, "loops", "sadie")
RECENT_BOARDS = 7          # how many recent sweeps count as "live" signal
MIN_MATCH_LEN = 6          # normalized company name must be at least this long to match (anti-junk)

sys.path.insert(0, os.path.join(REPO, "dashboard"))


def _norm(s):
    s = (s or "").lower()
    s = re.sub(r"\b(llc|inc|co|corp|ltd|the|company|services|service|group)\b", "", s)
    return re.sub(r"[^a-z0-9]", "", s)


def _next_id(prefix, items):
    n = max([int(re.sub(r"\D", "", x.get("id", "")) or 0) for x in items
             if x.get("id", "").startswith(prefix)] + [0])
    return f"{prefix}{n + 1}"


def _save(crm):
    json.dump(crm, open(CRM, "w"), indent=2, ensure_ascii=False)
    try:
        import melanie
        melanie.write_mirror(crm)     # regenerate crm/data.js (the dashboard's static mirror)
    except Exception:
        pass


# ── board parsing (signals live in the committed sweep boards) ──────────────────────────────
_LINE = re.compile(r"^- \*\*\[(?P<sig>.*?)\]\((?P<url>[^)]+)\)\*\* · (?P<vertical>[^·]*) · "
                   r"(?P<platform>[^·]*) · (?P<klass>[\w-]+) \(heat (?P<heat>\d+)\)", re.M)


def board_signals(last_n=RECENT_BOARDS):
    """Parse the last N sweep boards into signal dicts (newest board first, board order kept)."""
    out, seen = [], set()
    for path in sorted(glob.glob(os.path.join(BOARDS, "*_intent-sweep.md")), reverse=True)[:last_n]:
        date = os.path.basename(path)[:10]
        for m in _LINE.finditer(open(path, encoding="utf-8").read()):
            d = {k: v.strip() for k, v in m.groupdict().items()}
            if d["url"] in seen:
                continue
            seen.add(d["url"])
            d["date"] = date
            out.append(d)
    return out


def _sig_entry(sig, url, platform, date):
    return {"heat": "hot", "text": f'Sadie {date}: "{sig[:120]}" ({platform})',
            "url": url, "source": "sadie"}


# ── lane 1: attach to existing companies ────────────────────────────────────────────────────
def attach_matched(signals=None, dry_run=True):
    """Match signals against existing CRM companies (normalized-name substring in the signal text or
    author) and append to company.signals[]. Never creates rows. Returns [(company, sig_text), ...]."""
    signals = board_signals() if signals is None else signals
    crm = json.load(open(CRM))
    attached = []
    for c in crm.get("companies", []):
        key = _norm(c.get("name", ""))
        if len(key) < MIN_MATCH_LEN:
            continue
        have = {s.get("url") for s in c.get("signals", [])}
        for d in signals:
            hay = _norm(d.get("sig", "") + d.get("name", ""))
            if key in hay and d["url"] not in have:
                attached.append((c["name"], d["sig"][:80]))
                if not dry_run:
                    c.setdefault("signals", []).append(
                        _sig_entry(d["sig"], d["url"], d.get("platform", ""), d.get("date", "")))
                have.add(d["url"])
    if not dry_run and attached:
        _save(crm)
    return attached


# ── lane 2: gated promotion of an identified business ───────────────────────────────────────
def promote(url, company, vertical="", domain="", location="", contact="", email="", dry_run=True):
    """Create company + (optional) contact + prospect-stage deal for an identified business behind a
    Sadie signal. Skips if the company already exists (attach instead). Mirrors promote.py."""
    sig = next((d for d in board_signals(last_n=30) if d["url"] == url), None)
    if not sig:
        return {"error": f"signal url not found in the last 30 sweep boards: {url}"}
    crm = json.load(open(CRM))
    companies, contacts, deals = (crm.setdefault(k, []) for k in ("companies", "contacts", "deals"))
    if _norm(company) in {_norm(c.get("name", "")) for c in companies}:
        return {"error": f"'{company}' already in CRM — use --attach, not promote"}
    today = datetime.date.today().isoformat()
    if dry_run:
        return {"would_create": company, "signal": sig["sig"][:100]}
    cid = _next_id("c", companies)
    companies.append({"id": cid, "name": company, "vertical": vertical or sig.get("vertical", ""),
                      "size": "", "location": location, "domain": domain,
                      "source": f"sadie intent ({sig.get('platform', 'social')})",
                      # The one channel whose whole existence is the question "did listening
                      # ever produce a row a human worked?" — Sadie's owned number.
                      "channel": "intent-signal", "channelSource": "recorded",
                      "status": "prospect", "owner": "Reilly", "example": False,
                      "createdAt": _today(), "createdAtSource": "recorded",
                      "signals": [_sig_entry(sig["sig"], url, sig.get("platform", ""), sig.get("date", ""))]})
    if contact or email:
        contacts.append({"id": _next_id("p", contacts), "name": contact, "companyId": cid,
                         "role": "", "email": email, "phone": "", "lastTouch": today, "status": "new"})
    deals.append({"id": _next_id("d", deals), "name": f"{company} — intent signal",
                  # `prospect` is a retired rung (2026-08-07 restructure) — fixed 2026-08-25.
                  "companyId": cid, "useCase": "TBD — qualify on discovery call", "stage": "pre-convo",
                  "buildFee": None, "retainer": None, "value": 0,
                  "nextAction": "Verify the business + first touch (gated)", "nextDate": "",
                  "lastTouch": today, "owner": "Reilly", "stageSince": today,
                  "stageHistory": [{"stage": "pre-convo", "at": today, "source": "recorded"}]})
    _save(crm)
    return {"created": company, "companyId": cid}


if __name__ == "__main__":
    a = sys.argv[1:]
    commit = "--commit" in a
    get = lambda k: a[a.index(k) + 1] if k in a else ""
    if "--attach" in a:
        res = attach_matched(dry_run=not commit)
        verb = "attached" if commit else "would attach"
        print(f"{verb} {len(res)} signal(s):" if res else "no signals match existing CRM companies")
        for name, sig in res:
            print(f"  • {name} ← {sig}")
    elif "--promote" in a:
        res = promote(get("--signal-url"), get("--company"), vertical=get("--vertical"),
                      domain=get("--domain"), location=get("--location"),
                      contact=get("--contact"), email=get("--email"), dry_run=not commit)
        print(json.dumps(res, indent=2))
        sys.exit(1 if "error" in res else 0)
    else:  # --list: unmatched prospect-grade candidates for promotion
        crm = json.load(open(CRM))
        keys = [_norm(c.get("name", "")) for c in crm.get("companies", [])]
        keys = [k for k in keys if len(k) >= MIN_MATCH_LEN]
        cands = [d for d in board_signals()
                 if d.get("klass") in ("prospect", "business-complaint")
                 and not any(k in _norm(d.get("sig", "")) for k in keys)]
        print(f"{len(cands)} unmatched prospect-grade signal(s) (last {RECENT_BOARDS} sweeps) — "
              f"identify the business, then --promote:")
        for d in cands:
            print(f"  • [{d['date']} {d['platform']}] {d['sig'][:110]}\n    {d['url']}")
