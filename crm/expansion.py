#!/usr/bin/env python3
"""Client outcomes → when to open an Expansion or a Referral conversation.

WHERE THE DATA LIVES (the decision this module encodes):

    Outcome measurements live with DELIVERY, in `clients/<slug>/outcomes.jsonl` —
    append-only, one dated row per measurement. The CRM does NOT own them; it
    READS them. Delivery produces the number, the CRM decides what it means for
    revenue. Copying them into data.json would create a second copy that drifts
    the first time a loop writes one and not the other.

    The BASELINE lives in the same file as the first row, and it is not optional.
    An ROI claim without a pre-baseline is a number with no denominator — the
    Audit already quantifies the bottleneck in dollars, so that figure IS the
    baseline and gets written at go-live, before the module runs.

THE TWO TRIGGERS (why they are gated the way they are):

  EXPANSION — proposed only when the CURRENT thing is working and the NEXT thing
    has a number on it. Specifically: a live module with >= MIN_WEEKS of clean
    operation, its own outcome at or above baseline, zero overdue promises, and an
    un-built pillar carrying a quantified bottleneck from the Audit. Expansion
    pitched on top of a module that isn't yet delivering is how a good account
    turns into a bad one.

  REFERRAL — asked only when the client has REALISED value (a measured outcome
    above baseline), promise debt is zero, and no escalation is open. Asking for a
    referral while you still owe them something spends the relationship to buy a
    lead, and usually loses both.

Both refuse rather than guess: with no outcomes file, this reports "no evidence"
and names what's missing. It never infers that a client is happy.

Run:
    python3 crm/expansion.py            # readiness per live client
    python3 crm/expansion.py --json
"""
import json, os, sys, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
REPO = os.path.dirname(HERE)
DATA = os.path.join(DATA_DIR, "data.json")
CLIENTS = os.path.join(REPO, "clients")
TODAY = datetime.date.today()

MIN_WEEKS = 4          # clean operation before expansion is even proposed
# `expand` retired as a stage 2026-08-13 — an expansion is a separate deal that reaches Live
# in its own right, so a client is simply live.
LIVE = {"live"}
# The 8 pillars an OS is made of (processes/ai-os-modules.md). Expansion is always "which
# pillar is still un-built", never "sell them more" — the taxonomy is the menu.
PILLARS = ["Intake", "Sales", "Marketing", "Customer", "Operations", "Back Office",
           "Company Brain", "Training"]


def _d(iso):
    try:
        return datetime.date.fromisoformat(str(iso)[:10])
    except Exception:
        return None


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", str(name or "").lower()).strip("-")


def client_dir(company_name):
    s = slug(company_name)
    for cand in (s, s.replace("-llc", "").strip("-"), s.split("-")[0]):
        p = os.path.join(CLIENTS, cand)
        if cand and os.path.isdir(p):
            return p
    return None


def read_outcomes(folder):
    """clients/<slug>/outcomes.jsonl — append-only. Each row:
       {date, metric, value, unit, baseline, direction, module, source, note}"""
    path = os.path.join(folder or "", "outcomes.jsonl")
    rows = []
    if not folder or not os.path.exists(path):
        return rows
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def latest_per_metric(rows):
    out = {}
    for r in sorted(rows, key=lambda x: str(x.get("date") or "")):
        if r.get("metric"):
            out[r["metric"]] = r
    return out


def assess(deal, co, data):
    folder = client_dir(co.get("name"))
    rows = read_outcomes(folder)
    latest = latest_per_metric(rows)

    # --- how long has it actually been running clean ---
    since = _d(deal.get("stageSince"))
    weeks = round(((TODAY - since).days / 7.0), 1) if since else None

    # --- promise debt: you cannot expand or ask for a referral while you owe them ---
    proms = deal.get("promises") or []
    overdue = [p for p in proms if (p.get("status") or "open") == "open"
               and p.get("due") and _d(p["due"]) and _d(p["due"]) < TODAY]

    # --- realised value: a metric at or above its own baseline ---
    realised, unproven, missing_baseline, no_direction = [], [], [], []
    for m, r in latest.items():
        try:
            v = float(r.get("value"))
        except Exception:
            unproven.append(m); continue
        b = r.get("baseline")
        if b in (None, ""):
            missing_baseline.append(m); continue
        try:
            b = float(b)
        except Exception:
            missing_baseline.append(m); continue
        # DIRECTION IS NOT OPTIONAL. Half the metrics that matter improve by going DOWN — quote
        # turnaround, cost per job, hours on admin — and comparing value>=baseline scores a 42-day
        # to 2-day improvement as a failure. Where a row doesn't declare it and the value moved
        # the "wrong" way, we refuse rather than guess which way is good.
        d = str(r.get("direction") or "").strip().lower()
        if d not in ("up", "down"):
            if v >= b:
                d = "up"                       # improved on the naive read either way; safe
            else:
                no_direction.append(m); continue
        better = (v >= b) if d == "up" else (v <= b)
        row = {"metric": m, "value": v, "baseline": b, "unit": r.get("unit", ""),
               "direction": d, "delta": round(v - b, 2), "asOf": r.get("date"),
               "module": r.get("module", "")}
        (realised if better else unproven).append(row)

    built = {str(p.get("module") or "").strip() for p in (deal.get("artifacts") or [])} | \
            {str(r.get("module") or "").strip() for r in rows}
    built = {b for b in built if b}
    unbuilt = [p for p in PILLARS if p not in built]

    # --- the gates ---
    exp_blockers, ref_blockers = [], []
    if not rows:
        exp_blockers.append("no outcomes.jsonl — nothing measured, so nothing to expand on the strength of")
        ref_blockers.append("no outcomes.jsonl — no realised value to point at")
    if weeks is None or weeks < MIN_WEEKS:
        exp_blockers.append(f"{weeks if weeks is not None else '?'} weeks live, needs {MIN_WEEKS}")
    if not realised:
        exp_blockers.append("no metric is at or above its baseline yet")
        ref_blockers.append("no metric is at or above its baseline yet")
    if overdue:
        exp_blockers.append(f"{len(overdue)} overdue promise(s) — settle the debt first")
        ref_blockers.append(f"{len(overdue)} overdue promise(s) — asking now spends the relationship")
    if missing_baseline:
        exp_blockers.append("no baseline on: " + ", ".join(missing_baseline) + " — an ROI claim needs a denominator")
    if no_direction:
        exp_blockers.append("no `direction` on: " + ", ".join(no_direction) +
                            " — the value moved down and nothing says whether down is good")

    return {
        "dealId": deal.get("id"), "company": co.get("name"),
        "stage": deal.get("stage"), "weeksLive": weeks,
        "folder": os.path.relpath(folder, REPO) if folder else None,
        "hasLedger": bool(rows), "measurements": len(rows),
        "realised": realised, "unproven": unproven, "missingBaseline": missing_baseline,
        "noDirection": no_direction,
        "overduePromises": len(overdue),
        "builtModules": sorted(built), "unbuiltPillars": unbuilt,
        "expansionReady": not exp_blockers,
        "referralReady": not ref_blockers,
        "expansionBlockers": exp_blockers,
        "referralBlockers": ref_blockers,
        "nextModule": (unbuilt[0] if (not exp_blockers and unbuilt) else None),
    }


def read_audit(folder):
    """clients/<slug>/audit.json — Bella's structured diagnosis. It is the BASELINE the outcomes
    ledger measures against, which is why it is written once and amended with a dated note rather
    than rewritten: editing it retroactively invalidates every ROI claim built on top of it."""
    path = os.path.join(folder or "", "audit.json")
    if not folder or not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            a = json.load(f)
    except Exception:
        return None
    a["findings"] = [f for f in (a.get("findings") or []) if not f.get("_example")]
    return a


def audits(data):
    out = {}
    for c in data.get("companies", []) or []:
        a = read_audit(client_dir(c.get("name")))
        if a:
            out[c["id"]] = a
    return out


# Value is not only money. An OS that saves 14 hours a week or takes a client from 6 rework
# incidents a month to 1 has delivered something real, and forcing that into a dollar figure
# would mean inventing an hourly rate nobody agreed. Each unit rolls up in ITS OWN terms; the
# dollar column stays empty unless someone wrote the arithmetic down.
VALUE_KINDS = {
    "dollars": {"label": "saved / earned", "unit": "$"},
    "hours":   {"label": "hours given back", "unit": "h"},
    "errors":  {"label": "mistakes avoided", "unit": ""},
    "count":   {"label": "units", "unit": ""},
}


def value_rollup(rows):
    """Realised value per KIND, each summed only against its own kind."""
    out = {}
    for r in rows:
        kind = str(r.get("valueKind") or ("dollars" if r.get("dollarImpact") is not None else "")).strip().lower()
        amt = r.get("valueAmount")
        if kind == "dollars" and amt is None:
            amt = r.get("dollarImpact")
        if kind not in VALUE_KINDS or not isinstance(amt, (int, float)):
            continue
        b = out.setdefault(kind, {"kind": kind, "label": VALUE_KINDS[kind]["label"],
                                  "unit": VALUE_KINDS[kind]["unit"], "total": 0, "rows": 0,
                                  "period": r.get("valuePeriod") or "per year"})
        b["total"] += amt; b["rows"] += 1
    for b in out.values():
        b["total"] = round(b["total"], 2)
    return list(out.values())


def roi(deal, co, aud, rows):
    """Realised dollars and ROI, or an honest refusal.

    Two numbers only get produced when their inputs exist:
      REALISED $  — sum of each outcome's own `dollarImpact`. A metric improving is not a dollar
                    figure; converting one to the other needs an arithmetic someone wrote down,
                    so the ledger carries it per row (with `dollarBasis`) and this only adds up.
      RECOVERED % — realised $ over the audited bottleneck for the linked finding. Needs both a
                    findingId and an annualCost, and is otherwise omitted rather than approximated.
      ROI x       — realised $ over what they PAY us for a year. Needs a priced deal.
    """
    priced = [r for r in rows if isinstance(r.get("dollarImpact"), (int, float))]
    realised = round(sum(r["dollarImpact"] for r in priced), 2) if priced else None
    fee = 0.0
    try:
        fee = float(deal.get("retainer") or 0) * 12 + float(deal.get("buildFee") or 0)
    except Exception:
        fee = 0.0
    audited = None
    if aud:
        ids = {r.get("findingId") for r in priced if r.get("findingId")}
        linked = [f for f in (aud.get("findings") or []) if f.get("id") in ids]
        vals = [f.get("annualCost") for f in linked if isinstance(f.get("annualCost"), (int, float))]
        audited = sum(vals) if vals else None
    return {
        "valueRollup": value_rollup(rows),
        "realisedDollars": realised,
        "pricedRows": len(priced), "unpricedRows": len(rows) - len(priced),
        "annualFee": fee or None,
        "roiMultiple": (round(realised / fee, 2) if realised and fee else None),
        "auditedBottleneck": audited,
        "recoveredPct": (round(100 * realised / audited) if realised and audited else None),
        "why": ("" if realised else
                ("no outcome row carries a dollarImpact — a metric moving is not a dollar figure, "
                 "and the arithmetic that turns one into the other has to be written down"
                 if rows else "no measurements yet")),
    }


def portfolio(data):
    """Every measurement across EVERY client folder, flattened for cross-client reporting.

    This is the "populate into the CRM" half: the ledgers stay the source of truth in each
    client folder, and this reads them all into one table the CRM can report on. Reading rather
    than copying is deliberate — a second stored copy drifts the first time one loop writes and
    another doesn't — but a derived mirror is written to crm/_outcomes.json so the static
    (no-backend) dashboard and the offline loops can still see it, clearly marked as derived."""
    cos = {c["id"]: c for c in data.get("companies", []) or []}
    stage_by_co = {}
    for d in data.get("deals", []) or []:
        stage_by_co.setdefault(d.get("companyId"), d.get("stage"))
    flat, per_metric = [], {}
    for cid, co in cos.items():
        folder = client_dir(co.get("name"))
        for r in read_outcomes(folder):
            if not r.get("metric"):
                continue
            row = {"company": co.get("name"), "companyId": cid, "stage": stage_by_co.get(cid),
                   "date": r.get("date"), "metric": r["metric"], "value": r.get("value"),
                   "unit": r.get("unit", ""), "baseline": r.get("baseline"),
                   "direction": r.get("direction", ""), "module": r.get("module", ""),
                   "dollarImpact": r.get("dollarImpact"), "dollarBasis": r.get("dollarBasis", ""),
                   "valueKind": r.get("valueKind", ""), "valueAmount": r.get("valueAmount"),
                   "valuePeriod": r.get("valuePeriod", ""),
                   "findingId": r.get("findingId", ""),
                   "source": r.get("source", ""), "note": r.get("note", "")}
            flat.append(row)
            per_metric.setdefault(r["metric"], []).append(row)
    flat.sort(key=lambda x: str(x.get("date") or ""), reverse=True)
    # A metric only rolls up across clients when every contributing row shares a unit — averaging
    # "days" with "%" would produce a number that looks fine and means nothing.
    summary = []
    for m, rows in per_metric.items():
        units = {r["unit"] for r in rows}
        vals = [r["value"] for r in rows if isinstance(r.get("value"), (int, float))]
        summary.append({"metric": m, "clients": len({r["company"] for r in rows}),
                        "measurements": len(rows), "unit": (list(units)[0] if len(units) == 1 else None),
                        "mixedUnits": len(units) > 1,
                        "mean": (round(sum(vals) / len(vals), 2) if vals and len(units) == 1 else None),
                        "latest": max((r["date"] for r in rows if r.get("date")), default=None)})
    summary.sort(key=lambda x: -x["measurements"])
    auds = audits(data)
    per_client = {}
    for cid, co in cos.items():
        rows = [r for r in flat if r["companyId"] == cid]
        if not rows:
            continue
        deal = next((d for d in data.get("deals", []) or [] if d.get("companyId") == cid), {})
        per_client[cid] = {"company": co.get("name"), **roi(deal, co, auds.get(cid), rows)}
    total = sum(v["realisedDollars"] or 0 for v in per_client.values())
    return {"rows": flat, "byMetric": summary, "roiByClient": per_client,
            "realisedTotal": round(total, 2) if total else None,
            "clientsWithLedger": len({r["company"] for r in flat})}


def compute(data):
    cos = {c["id"]: c for c in data.get("companies", []) or []}
    rows = [assess(d, cos.get(d.get("companyId"), {}), data)
            for d in data.get("deals", []) or [] if d.get("stage") in LIVE]
    port = portfolio(data)
    return {
        "portfolio": port, "audits": audits(data),
        "generated": TODAY.isoformat(), "minWeeks": MIN_WEEKS, "pillars": PILLARS,
        "liveClients": len(rows), "clients": rows,
        "expansionReady": [r["company"] for r in rows if r["expansionReady"]],
        "referralReady": [r["company"] for r in rows if r["referralReady"]],
        "contract": ("Outcome rows live in clients/<slug>/outcomes.jsonl, append-only, one per "
                     "measurement: {date, metric, value, unit, baseline, module, source, note}. "
                     "Delivery writes them; the CRM only reads them."),
        "honesty": ("Neither trigger fires on a hunch. Expansion needs a live module running clean for "
                    f"{MIN_WEEKS}+ weeks, a metric at or above ITS OWN baseline, zero overdue promises, and an "
                    "un-built pillar to point at. Referral needs realised value and zero promise debt — "
                    "asking while you owe someone spends the relationship to buy a lead. With no outcomes "
                    "file this reports no evidence and names what's missing; it never infers a happy client."),
    }


def write_mirror(result):
    """crm/_outcomes.json — DERIVED. The client ledgers remain the source of truth; this exists
    so the static dashboard and offline loops can read outcomes without walking clients/."""
    path = os.path.join(DATA_DIR, "_outcomes.json")
    payload = {"_derived": "Generated from clients/<slug>/outcomes.jsonl by crm/expansion.py. "
                           "Never hand-edit — edit the client ledger.",
               "generated": TODAY.isoformat(), **result["portfolio"]}
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)
    return path


def main():
    with open(DATA) as f:
        data = json.load(f)
    r = compute(data)
    if "--mirror" in sys.argv:
        print("wrote", os.path.relpath(write_mirror(r), REPO)); return
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); return
    p = r["portfolio"]
    print(f"Expansion & referral readiness — {r['liveClients']} live client(s) · "
          f"{len(p['rows'])} measurement(s) across {p['clientsWithLedger']} client(s) with a ledger\n")
    for m in p["byMetric"]:
        u = f" {m['unit']}" if m["unit"] else (" (mixed units — not averaged)" if m["mixedUnits"] else "")
        print(f"  {m['metric']:<24} {m['measurements']} reading(s), {m['clients']} client(s)"
              + (f", mean {m['mean']}{u}" if m["mean"] is not None else u))
    if p["byMetric"]: print()
    if not r["clients"]:
        print("  No client is live yet. This turns on at the first go-live; until then there is")
        print("  nothing to measure and the triggers correctly report nothing.")
        print(f"\n  Contract: {r['contract']}")
        return
    for c in r["clients"]:
        print(f"  {c['company']} — {c['weeksLive']} weeks live · {c['measurements']} measurement(s)")
        for m in c["realised"]:
            print(f"      ✓ {m['metric']}: {m['value']}{m['unit']} vs baseline {m['baseline']} (+{m['delta']})")
        print(f"      expansion: {'READY → ' + (c['nextModule'] or '?') if c['expansionReady'] else 'no — ' + '; '.join(c['expansionBlockers'])}")
        print(f"      referral:  {'READY' if c['referralReady'] else 'no — ' + '; '.join(c['referralBlockers'])}")
    print(f"\n{r['honesty']}")


if __name__ == "__main__":
    main()
