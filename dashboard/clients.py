#!/usr/bin/env python3
"""The Clients view — one row per engagement, every source joined.

the Founder's question (2026-08-07): "six months out, 15 clients active — where do I go to see
status, finances, contracts, and what's going on?"  Answer today was: nowhere. HQ's Delivery
tab renders delivery *agents*, not clients, and `dashboard/data.json` has no clients key.

DESIGN RULES
1. Derived, never hand-kept — same contract as board.py. Every field traces to a file whose
   owner already maintains it.
2. Honest at zero live clients. This ships while nothing is signed, so it reads every folder
   in clients/ (three real pre-signature engagements with real cost ledgers) and scores
   GO-LIVE READINESS instead of pretending to health. When the first deal goes live the same
   row switches to health scoring with no rebuild.
3. Never invent a number. cost.md rows carry values like "~$15-25", "unknown", "2 credits".
   Those are reported as a range with an unpriced count — never silently summed to a
   confident total. Margin is computed only when BOTH sides are real, and the reason it
   isn't computable is displayed instead of a blank.

Sources
  crm/data.json ................. stage, value, owner, last touch, next action
  clients/<slug>/cost.md ........ the spend ledger (phase-split)
  clients/<slug>/ledger/*.jsonl . actions, evals, incidents, outcomes, autonomy events
  clients/<slug>/contract.md .... the executed-contract register (absent = said so, loudly)
  clients/<slug>/*.md ........... unfilled [[PLACEHOLDER]] count — "don't ship a placeholder"
  finance/revenue.md ............ invoiced + paid, per client
  loops/customer-health/<latest>. the weekly health artifact, when one exists

Read-only. Exposed as GET /api/clients.
"""
import os, re, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: YOURCO_DATA_ROOT redirects every source read below to the sandbox tree.
ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.dirname(HERE)
PLAYGROUND = bool(os.environ.get("YOURCO_DATA_ROOT"))
CLIENTS = os.path.join(ROOT, "clients")

# CRM ladder -> where the engagement sits. Only `live`/`expand` get health scoring.
LIVE_STAGES = {"live", "expand", "expansion"}
SOLD_STAGES = {"signed", "build"} | LIVE_STAGES
MONEY_RE = re.compile(r"\$\s?([\d,]+(?:\.\d+)?)")
# Ledger rows are written as ranges — "~$15-25", "~$15–25 addl". Only the first figure carries
# a "$", so MONEY_RE alone collapses the range to its low end and the high estimate reads too
# cheap. Match the range form first, singles second.
RANGE_RE = re.compile(r"\$\s?([\d,]+(?:\.\d+)?)\s*[-–—]\s*([\d,]+(?:\.\d+)?)")
PLACEHOLDER_RE = re.compile(r"\[\[[^\]]{2,60}\]\]")


def _amounts(cell):
    """Every dollar figure in a ledger cell -> (low, high). Empty when nothing is priced."""
    vals = []
    for lo, hi in RANGE_RE.findall(cell or ""):
        vals += [float(lo.replace(",", "")), float(hi.replace(",", ""))]
    if not vals:
        vals = [float(n.replace(",", "")) for n in MONEY_RE.findall(cell or "")]
    return (min(vals), max(vals)) if vals else None


def _read(p):
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _load(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _age(d):
    if not d:
        return None
    m = re.search(r"(\d{4}-\d{2}-\d{2})", str(d))
    if not m:
        return None
    try:
        return (datetime.date.today() - datetime.date.fromisoformat(m.group(1))).days
    except ValueError:
        return None


def _slug_words(s):
    return set(re.sub(r"[^a-z0-9 ]", " ", (s or "").lower()).split())


# --------------------------------------------------------------------------
# cost.md — the spend ledger
# --------------------------------------------------------------------------
def read_cost(folder):
    """Parse the append-only ledger. Returns a low/high range plus an unpriced count, because
    real rows say '~$15-25', 'unknown', and '2 credits' — summing those to one confident
    number would be the fabrication this OS keeps warning about."""
    md = _read(os.path.join(folder, "cost.md"))
    if not md:
        return {"rows": 0, "low": 0.0, "high": 0.0, "unpriced": 0, "phases": {}, "pricing": None}
    pricing = None
    m = re.search(r"\*\*Pricing in effect:\*\*\s*(.+)", md)
    if m:
        p = re.sub(r"\s+", " ", m.group(1)).strip()
        pricing = None if "[[" in p and p.count("[[") >= 2 else p

    rows = low = high = unpriced = 0
    phases = {}
    in_ledger = False
    for ln in md.splitlines():
        if re.match(r"^\s*\|\s*Date\s*\|", ln, re.I):
            in_ledger = True
            continue
        if in_ledger and not ln.strip().startswith("|"):
            if ln.strip().startswith("#"):
                in_ledger = False
            continue
        if not in_ledger or not ln.strip().startswith("|"):
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 6 or all(re.fullmatch(r":?-{2,}:?", x) for x in c if x):
            continue
        if not re.match(r"\d{4}-\d{2}-\d{2}", c[0]):
            continue
        rows += 1
        phase = (c[1] or "?").lower()
        phases[phase] = phases.get(phase, 0) + 1
        amt = _amounts(c[4])
        if amt:
            low += amt[0]
            high += amt[1]
        else:
            unpriced += 1
    return {"rows": rows, "low": round(low, 2), "high": round(high, 2),
            "unpriced": unpriced, "phases": phases, "pricing": pricing}


# --------------------------------------------------------------------------
# ledger/*.jsonl — the moat layer's own record
# --------------------------------------------------------------------------
def read_ledger(folder):
    """The customer-health trigger is an **unaddressed** failed eval, not a lifetime count.
    A gate that failed in March and has passed every month since is a gate that got fixed —
    counting it forever would paint every mature engagement permanently red, which is exactly
    what the first cut of this did. So fails are tracked per (module, gate) and only the
    LATEST result for each counts."""
    d = os.path.join(folder, "ledger")
    out = {"files": 0, "actions": 0, "evalsPass": 0, "evalsFail": 0, "evalsFailOpen": 0,
           "incidentsOpen": 0, "outcomes": 0, "promotions": 0, "latest": None, "openGates": []}
    try:
        names = [f for f in os.listdir(d) if re.fullmatch(r"\d{4}-\d{2}\.jsonl", f)]
    except OSError:
        return out
    gate_latest = {}  # (module, gate) -> (ts, result)
    for n in sorted(names):
        out["files"] += 1
        out["latest"] = n[:-6]
        for ln in _read(os.path.join(d, n)).splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            t = r.get("record_type")
            if t == "action_record":
                out["actions"] += 1
            elif t == "eval_record":
                passed = r.get("result") == "pass"
                out["evalsPass" if passed else "evalsFail"] += 1
                k = (r.get("module") or "", r.get("gate_name") or "")
                ts = r.get("ts") or ""
                if k not in gate_latest or ts >= gate_latest[k][0]:
                    gate_latest[k] = (ts, r.get("result"))
            elif t == "incident_record":
                if not r.get("resolved_ts"):
                    out["incidentsOpen"] += 1
            elif t == "outcome_record":
                out["outcomes"] += 1
            elif t == "autonomy_event":
                out["promotions"] += 1
    openg = sorted(f"{m}/{g}" for (m, g), (_, res) in gate_latest.items() if res != "pass")
    out["evalsFailOpen"] = len(openg)
    out["openGates"] = openg[:6]
    return out


# --------------------------------------------------------------------------
# contract.md — the executed-contract register
# --------------------------------------------------------------------------
CONTRACT_FIELDS = ["Status", "Signed", "Effective", "Initial term", "Renews",
                   "Notice required", "Notice deadline", "DPA", "BAA", "Counsel-reviewed"]


def read_contract(folder):
    """Absent register -> `present:false`, which the UI renders as a red row rather than a
    blank. The engagement agreement §3 auto-renews monthly on 30 days' notice; at 15 clients
    that is 15 rolling notice windows, and an uncaptured renewal date is captured never."""
    p = os.path.join(folder, "contract.md")
    md = _read(p)
    if not md:
        return {"present": False, "fields": {}, "unfilled": [], "renewalDays": None}
    fields, unfilled = {}, []
    for k in CONTRACT_FIELDS:
        m = re.search(r"^\|\s*" + re.escape(k) + r"\s*\|\s*(.+?)\s*\|", md, re.M | re.I)
        v = (m.group(1).strip() if m else "")
        if not v or "[[" in v or v in ("—", "-", "TBD"):
            unfilled.append(k)
        else:
            fields[k] = v
    days = None
    dl = fields.get("Notice deadline")
    if dl:
        a = _age(dl)
        days = None if a is None else -a  # negative age = days remaining
    return {"present": True, "fields": fields, "unfilled": unfilled, "renewalDays": days}


# --------------------------------------------------------------------------
# finance/revenue.md — invoiced vs paid, matched by client name
# --------------------------------------------------------------------------
def revenue_by_client():
    md = _read(os.path.join(ROOT, "finance", "revenue.md"))
    out = {}
    for ln in md.splitlines():
        if not ln.strip().startswith("|"):
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 7 or c[1].lower() in ("client", "—", "-", ""):
            continue
        nums = MONEY_RE.findall(c[3])
        amt = float(nums[0].replace(",", "")) if nums else 0.0
        k = c[1].lower()
        r = out.setdefault(k, {"invoiced": 0.0, "paid": 0.0, "rows": 0})
        r["rows"] += 1
        r["invoiced"] += amt
        if (c[6] or "").lower().startswith("paid") or c[5] not in ("", "—", "-"):
            r["paid"] += amt
    return out


# --------------------------------------------------------------------------
# readiness — the customer-health loop's own pre-go-live requirements
# --------------------------------------------------------------------------
def readiness(folder, deal):
    """Straight from loops/customer-health §'Pre-engagement readiness' + the template's
    'every [[PLACEHOLDER]] must be filled before go-live' rule. This is the checklist that
    makes a health signal exist at all — without it the health loop has nothing to score."""
    has = lambda *p: os.path.exists(os.path.join(folder, *p))
    checks = [
        ("CRM deal at live", bool(deal) and (deal.get("stage") or "").lower() in LIVE_STAGES),
        ("Eval set (03_eval.md)", has("03_eval.md")),
        ("Weekly readout wired", has("weekly-readout.md") or os.path.isdir(os.path.join(folder, "weekly"))),
        ("Autonomy matrix", has("autonomy-matrix.md")),
        ("Client console", has("client-console.html")),
        ("Go-live plan", has("go-live.md")),
        ("Outcome ledger open", os.path.isdir(os.path.join(folder, "ledger"))),
        ("Contract on file", has("contract.md")),
    ]
    return [{"k": k, "ok": bool(v)} for k, v in checks]


def placeholders(folder):
    n, files = 0, 0
    for base, dirs, names in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "attachments", "assets")]
        for f in names:
            if not f.endswith(".md"):
                continue
            hits = PLACEHOLDER_RE.findall(_read(os.path.join(base, f)))
            if hits:
                files += 1
                n += len(hits)
    return {"count": n, "files": files}


def last_touched(folder):
    newest = 0
    for base, dirs, names in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules")]
        for f in names:
            try:
                newest = max(newest, os.path.getmtime(os.path.join(base, f)))
            except OSError:
                pass
    if not newest:
        return None
    return datetime.date.fromtimestamp(newest).isoformat()


# --------------------------------------------------------------------------
# assemble
# --------------------------------------------------------------------------
def _match_deal(slug, name, deals, companies):
    """Match a folder to its CRM deal on word overlap — folders are slugs ('sample-client'),
    CRM names are prose ('Sample Client — Installation Proposal Automation')."""
    want = _slug_words(slug.replace("-", " ")) | _slug_words(name)
    want -= {"the", "llc", "inc", "co", "and"}
    best, score = None, 0
    for d in deals:
        hay = _slug_words(d.get("name", "")) | _slug_words(companies.get(d.get("companyId"), ""))
        s = len(want & hay)
        if s > score:
            best, score = d, s
    return best if score >= 1 else None


def build():
    crm = _load(os.path.join(ROOT, "crm", "data.json")) or {}
    deals = crm.get("deals", []) or []
    companies = {c.get("id"): c.get("name", "") for c in crm.get("companies", []) or []}
    labels = {s.get("key"): s.get("label", s.get("key")) for s in crm.get("stages", []) or []}
    rev = revenue_by_client()

    try:
        slugs = sorted(d for d in os.listdir(CLIENTS)
                       if os.path.isdir(os.path.join(CLIENTS, d)) and not d.startswith("_"))
    except OSError:
        slugs = []

    rows = []
    for slug in slugs:
        folder = os.path.join(CLIENTS, slug)
        readme = _read(os.path.join(folder, "_README.md"))
        m = re.search(r"^#\s+(.+)$", readme, re.M)
        name = re.sub(r"\s*—.*$", "", m.group(1)).strip() if m else slug.replace("-", " ").title()

        deal = _match_deal(slug, name, deals, companies)
        stage = (deal.get("stage") or "").lower() if deal else ""
        cost = read_cost(folder)
        ledger = read_ledger(folder)
        contract = read_contract(folder)
        checks = readiness(folder, deal)
        ready = sum(1 for c in checks if c["ok"])
        ph = placeholders(folder)
        touched = last_touched(folder)
        money = rev.get(name.lower()) or rev.get(slug.replace("-", " ")) or {"invoiced": 0.0, "paid": 0.0, "rows": 0}

        is_live = stage in LIVE_STAGES
        # Margin only when both sides are real. Otherwise say why, don't show a blank.
        if money["paid"] > 0 and cost["high"] > 0:
            margin = {"value": round(money["paid"] - cost["high"], 2),
                      "note": f"paid ${money['paid']:,.0f} − spend high-estimate ${cost['high']:,.0f}"}
        else:
            why = "no revenue booked" if money["paid"] <= 0 else "no priced spend rows"
            margin = {"value": None, "note": f"not computable — {why}"}

        if is_live:
            flags = []
            if ledger["incidentsOpen"]:
                flags.append(f"{ledger['incidentsOpen']} unresolved incident(s)")
            if ledger["evalsFailOpen"]:
                flags.append(f"{ledger['evalsFailOpen']} gate(s) still failing: " + ", ".join(ledger["openGates"]))
            touch_age = _age((deal or {}).get("lastTouch"))
            if (touch_age or 0) > 14:  # parenthesised: `x or 0 > 14` binds as `x or (0>14)`
                flags.append(f"no touch in {touch_age}d")
            hard = ledger["incidentsOpen"] or ledger["evalsFailOpen"]
            health = "red" if hard else ("yellow" if flags else "green")
            status, statusNote = health, "; ".join(flags) or "no open incidents, every eval gate currently passing"
        else:
            status = "pre-live"
            statusNote = f"{ready}/{len(checks)} go-live requirements met"

        rows.append({
            "slug": slug, "name": name,
            "stage": labels.get(stage, stage) or "no CRM deal",
            "stageKey": stage, "isLive": is_live,
            "value": (deal or {}).get("value") or "",
            "owner": (deal or {}).get("owner") or "the Founder",
            "lastTouch": (deal or {}).get("lastTouch") or "",
            "lastTouchDays": _age((deal or {}).get("lastTouch")),
            "nextAction": (deal or {}).get("nextAction") or "",
            "nextDate": (deal or {}).get("nextDate") or "",
            "nextDue": _age((deal or {}).get("nextDate")),
            "touched": touched, "touchedDays": _age(touched),
            "cost": cost, "ledger": ledger, "contract": contract,
            "revenue": money, "margin": margin,
            "checks": checks, "ready": ready, "readyOf": len(checks),
            "placeholders": ph, "status": status, "statusNote": statusNote,
        })

    rows.sort(key=lambda r: (not r["isLive"], -(r["ready"]), r["name"]))

    live = [r for r in rows if r["isLive"]]
    # HQ's goal strip counts CRM stage `live` ONLY — confirmed correct by the Founder 2026-08-07.
    # This view counts live + expand, because an expansion is still a running engagement to
    # operate. Both are right; showing only the combined figure made them look like they
    # disagreed (12 vs 15 in the sandbox), so the split is surfaced rather than reconciled away.
    on_ladder = sum(1 for r in live if r["stageKey"] == "live")
    expanding = len(live) - on_ladder
    spendLow = sum(r["cost"]["low"] for r in rows)
    spendHigh = sum(r["cost"]["high"] for r in rows)
    unpriced = sum(r["cost"]["unpriced"] for r in rows)
    return {
        "clients": rows,
        "headline": {
            "folders": len(rows), "live": len(live),
            "liveStage": on_ladder, "expanding": expanding,
            "preLive": len(rows) - len(live),
            "mrrPaid": round(sum(r["revenue"]["paid"] for r in rows), 2),
            "spendLow": round(spendLow, 2), "spendHigh": round(spendHigh, 2),
            "unpricedRows": unpriced,
            "contractsOnFile": sum(1 for r in rows if r["contract"]["present"]),
            "openIncidents": sum(r["ledger"]["incidentsOpen"] for r in rows),
            "placeholders": sum(r["placeholders"]["count"] for r in rows),
        },
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


if __name__ == "__main__":
    b = build()
    h = b["headline"]
    print(f"{h['folders']} engagement folders — {h['live']} live, {h['preLive']} pre-live")
    print(f"spend ~${h['spendLow']:,.0f}-${h['spendHigh']:,.0f} ({h['unpricedRows']} unpriced rows) · "
          f"revenue ${h['mrrPaid']:,.0f} · contracts on file {h['contractsOnFile']}/{h['folders']} · "
          f"open incidents {h['openIncidents']} · placeholders {h['placeholders']}")
    for r in b["clients"]:
        print(f"\n  {r['name']}  [{r['stage']}]  {r['status']} — {r['statusNote']}")
        print(f"    spend ~${r['cost']['low']:,.0f}-${r['cost']['high']:,.0f} over {r['cost']['rows']} rows"
              f" ({r['cost']['unpriced']} unpriced) · margin: {r['margin']['note']}")
        print(f"    contract: {'on file' if r['contract']['present'] else 'NONE ON FILE'} · "
              f"placeholders {r['placeholders']['count']} · last touched {r['touched']}")
        print("    missing: " + (", ".join(c["k"] for c in r["checks"] if not c["ok"]) or "nothing"))
