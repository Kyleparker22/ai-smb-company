#!/usr/bin/env python3
"""Price events — the instrument that answers "is the price right?" with evidence.

Munger's test for a moat is pricing power: if you need a prayer meeting before raising
prices, you have a terrible business. yourco could not run that test at all, because
nothing in the CRM recorded a price event. Sample Client sat unsigned at $1,000/mo against
a $3,000 Core floor and no field anywhere says whether price was the reason.

This module reads `deals[].priceEvents[]` — an append-only log of what was actually said
about money — and reports the four things a price decision needs:

  1. ACCEPTANCE WITHOUT PUSHBACK. The single strongest signal you are underpriced. A quote
     accepted with no counter, no silence, no "can you do better" is a quote that was too
     low. Ramanujam's whole method rests on this; it is also the cheapest datum to collect
     and nobody collects it.
  2. THE DISCOUNT LADDER. Every concession, who asked, and what it bought. A discount that
     bought nothing (no signature, no faster close) is a price cut you gave away.
  3. RESISTANCE BY SEGMENT. Where the pushback clusters — vertical, size, source. Price is
     a proxy for value, and value differs by segment; one blended price hides that.
  4. THE FLOOR TEST. Of deals quoted at or below the Core floor, how many still stalled?
     If they stall anyway, price was never the objection and cutting it is pure margin loss.

REFUSAL RULES — this module is about money and will not guess:
  · Under MIN_EVENTS priced deals it reports "insufficient" and states how many more are
    needed. It never renders a trend from two data points.
  · "Accepted without pushback" is a HUMAN-RECORDED field, never inferred from the absence
    of a counter-event. Absence of a record is not a record of absence — the person may
    simply not have logged it, and treating silence as enthusiasm is exactly how a company
    talks itself into believing it is priced correctly.
  · It never recommends a specific new price. It reports the evidence; Polo prices, the Founder
    locks (agents/polo/_README.md).

Run:
    python3 crm/pricing_power.py
    python3 crm/pricing_power.py --json
"""
import json, os, sys, datetime, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
DATA = os.path.join(DATA_DIR, "data.json")
TODAY = datetime.date.today()

MIN_EVENTS = 5          # priced deals before any pattern is claimed
CORE_FLOOR = 3000       # the OS Core floor (pricing/v0/os-tiers.md) — quoted below this is a discount

# The vocabulary. Deliberately small: a long enum produces inconsistent logging, and an
# inconsistent log is worse than none because it looks complete.
KINDS = {
    "quoted":     "we named a number",
    "countered":  "they named a different one",
    "discounted": "we moved down",
    "accepted":   "they said yes at the number",
    "declined":   "they said no at the number",
    "walked":     "we declined to go lower",
}


def _d(iso):
    try:
        return datetime.date.fromisoformat(str(iso)[:10])
    except Exception:
        return None


def holders(data):
    for d in data.get("deals", []) or []:
        yield d, False
    for c in data.get("closed", []) or []:
        yield c, True


def events(data):
    """Flatten every price event, joined to its deal + company."""
    cos = {c["id"]: c for c in data.get("companies", []) or []}
    rows = []
    for h, closed in holders(data):
        co = cos.get(h.get("companyId"), {})
        for e in h.get("priceEvents") or []:
            rows.append({
                "dealId": h.get("id"), "company": co.get("name") or h.get("name"),
                "vertical": co.get("vertical") or "", "source": co.get("source") or "",
                "size": co.get("size"),
                "date": e.get("date"), "kind": (e.get("kind") or "").lower(),
                "amount": float(e.get("amount") or 0), "by": e.get("by") or "",
                "note": e.get("note") or "",
                # human-recorded only — see the refusal rules in the docstring
                "noPushback": bool(e.get("noPushback")),
                "stage": h.get("stage"), "closed": closed, "outcome": h.get("outcome"),
            })
    rows.sort(key=lambda r: str(r["date"]))
    return rows


def per_deal(data, rows):
    """One record per deal that has any price history — the ladder for that negotiation."""
    by = {}
    for r in rows:
        b = by.setdefault(r["dealId"], {"dealId": r["dealId"], "company": r["company"],
                                        "vertical": r["vertical"], "events": [],
                                        "closed": r["closed"], "outcome": r["outcome"],
                                        "stage": r["stage"]})
        b["events"].append(r)
    out = []
    for b in by.values():
        evs = b["events"]
        quotes = [e for e in evs if e["kind"] == "quoted"]
        first = quotes[0]["amount"] if quotes else None
        finals = [e for e in evs if e["kind"] in ("accepted", "discounted")]
        final = finals[-1]["amount"] if finals else (quotes[-1]["amount"] if quotes else None)
        concession = (first - final) if (first and final and final < first) else 0
        b.update({
            "firstQuote": first, "finalNumber": final,
            "concession": concession,
            "concessionPct": round(concession / first * 100, 1) if (first and concession) else 0,
            "counters": sum(1 for e in evs if e["kind"] == "countered"),
            "noPushback": any(e["noPushback"] for e in evs if e["kind"] in ("quoted", "accepted")),
            "belowFloor": bool(first and first < CORE_FLOOR),
            "won": b["outcome"] == "won",
            "resolved": bool(b["closed"]),
        })
        out.append(b)
    out.sort(key=lambda b: -(b["firstQuote"] or 0))
    return out


def compute(data=None):
    if data is None:
        with open(DATA) as f:
            data = json.load(f)
    rows = events(data)
    deals = per_deal(data, rows)
    priced = [d for d in deals if d["firstQuote"]]
    n = len(priced)

    out = {
        "generated": TODAY.isoformat(), "coreFloor": CORE_FLOOR, "kinds": KINDS,
        "events": len(rows), "pricedDeals": n, "deals": deals, "minEvents": MIN_EVENTS,
    }

    if n < MIN_EVENTS:
        out.update({
            "status": "insufficient", "needs": MIN_EVENTS - n,
            "reading": (f"{n} deal(s) carry a recorded price. {MIN_EVENTS - n} more before this "
                        f"reports a pattern — a price decision made off {n} data point(s) is a "
                        f"guess wearing evidence's clothes."),
            "acceptedNoPushback": None, "medianConcessionPct": None, "floorTest": None,
            "bySegment": None,
        })
        # The one thing worth saying below the threshold: what is missing, per deal.
        out["gaps"] = [
            {"dealId": d.get("id"), "company": (next((c.get("name") for c in data.get("companies", [])
                                                      if c.get("id") == d.get("companyId")), None)
                                               or d.get("name")),
             "stage": d.get("stage"),
             "why": "no price event recorded — log the quote the day you send it, not later"}
            for d in (data.get("deals") or [])
            if not (d.get("priceEvents") or []) and d.get("stage") in
            ("demo-proposal", "signed-onboarding", "build-implementation", "testing", "live")
        ]
        return out

    # ---- the four reads ---------------------------------------------------------------
    npb = [d for d in priced if d["noPushback"]]
    concessions = [d["concessionPct"] for d in priced if d["concessionPct"] > 0]
    below = [d for d in priced if d["belowFloor"]]
    below_stalled = [d for d in below if not d["won"]]

    seg = {}
    for d in priced:
        k = d["vertical"] or "unspecified"
        s = seg.setdefault(k, {"segment": k, "n": 0, "counters": 0, "concessions": []})
        s["n"] += 1
        s["counters"] += d["counters"]
        if d["concessionPct"]:
            s["concessions"].append(d["concessionPct"])
    for s in seg.values():
        s["medianConcessionPct"] = round(statistics.median(s["concessions"]), 1) if s["concessions"] else 0
        s["resistance"] = round(s["counters"] / s["n"], 2)
        s.pop("concessions")

    # Discounts that bought nothing: we moved down and still did not win.
    wasted = [d for d in priced if d["concession"] > 0 and d["resolved"] and not d["won"]]

    out.update({
        "status": "measured",
        "acceptedNoPushback": {
            "n": len(npb), "of": n, "pct": round(len(npb) / n * 100),
            "deals": [d["company"] for d in npb],
            "reading": ("every quote met resistance — no evidence of underpricing"
                        if not npb else
                        f"{len(npb)} of {n} quotes were accepted with no pushback recorded. That is "
                        f"the strongest available signal the number is too low."),
        },
        "medianConcessionPct": round(statistics.median(concessions), 1) if concessions else 0,
        "wastedDiscounts": [{"company": d["company"], "gave": d["concession"],
                             "pct": d["concessionPct"]} for d in wasted],
        "floorTest": {
            "quotedBelowFloor": len(below), "ofWhichStalled": len(below_stalled),
            "reading": ("nothing quoted below the floor yet" if not below else
                        f"{len(below_stalled)} of {len(below)} deals quoted BELOW the ${CORE_FLOOR:,} "
                        f"floor stalled anyway — price was not the objection on those, and cutting "
                        f"further would be margin given away for nothing."),
        },
        "bySegment": sorted(seg.values(), key=lambda s: -s["resistance"]),
    })
    out["reading"] = (f"{n} priced deals · {out['acceptedNoPushback']['pct']}% accepted without "
                      f"pushback · median concession {out['medianConcessionPct']}%")
    return out


def main():
    r = compute()
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); return
    print(f"Price events — {r['events']} event(s) across {r['pricedDeals']} priced deal(s)\n")
    if r["status"] == "insufficient":
        print("  " + r["reading"])
        if r.get("gaps"):
            print(f"\n  {len(r['gaps'])} deal(s) past Demo and Proposal with NO price recorded:")
            for g in r["gaps"][:8]:
                print(f"    · {g['company']} ({g['stage']}) — {g['why']}")
        return
    print("  " + r["acceptedNoPushback"]["reading"])
    print(f"  median concession {r['medianConcessionPct']}%")
    print("  " + r["floorTest"]["reading"])
    if r["wastedDiscounts"]:
        print("\n  Discounts that bought nothing:")
        for w in r["wastedDiscounts"]:
            print(f"    · {w['company']} — gave ${w['gave']:,.0f} ({w['pct']}%) and still lost")
    print("\n  Resistance by segment (counters per deal):")
    for s in r["bySegment"]:
        print(f"    {s['segment'][:24]:<24} {s['resistance']:>5} counters/deal · "
              f"median concession {s['medianConcessionPct']}%  (n={s['n']})")
    print("\n  This reports evidence only. Polo prices, the Founder locks.")


if __name__ == "__main__":
    main()
