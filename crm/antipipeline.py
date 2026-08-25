#!/usr/bin/env python3
"""The anti-pipeline — deals the CRM recommends you DECLINE, with the evidence.

Every CRM optimises in one direction. Lead scoring ranks upward; forecasting weights toward
close; the whole instrument is built to help you win. Nothing anywhere asks the inverted
question Munger would insist on: **which of these should we not take?**

For yourco that question is unusually load-bearing, for a reason most consultancies do not
share: **yourco absorbs the model and infra spend.** A bad-fit client is not a break-even
distraction, it is negative margin — you pay to serve someone you are failing. Add a solo
delivery bench (crm/capacity.py) and every wrong yes costs a right one.

So this is the anti-pipeline: a ranked list of open deals with the case AGAINST each, built
only from recorded evidence, plus the churn hypothesis a human wrote down before signing.

THE CHURN HYPOTHESIS. Before a deal reaches Signed, someone records what would make this a
bad client — `deal.churnHypothesis = {risks:[{key, note, severity}], recordedOn, by}`. This
is a pre-mortem, and its value is that it is written while you still want the deal. A risk
named after the fact is a rationalisation; the same risk named before signature is a test.

REFUSAL RULES:
  · It NEVER auto-declines. It ranks and argues; a human declines. Walking away from revenue
    is exactly the class of judgement that stays with the Founder.
  · Every flag cites a field or a count. A flag that cannot name its evidence is not shown —
    "feels risky" is not a finding.
  · Absence of evidence never becomes a flag ON someone. An unfilled mirror means we did not
    do the work, not that the buyer is bad, and it is reported as OUR gap.

Run:
    python3 crm/antipipeline.py
    python3 crm/antipipeline.py --json
"""
import json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
REPO = os.path.dirname(HERE)
DATA = os.path.join(DATA_DIR, "data.json")
TODAY = datetime.date.today()

CORE_FLOOR = 3000     # pricing/v0/os-tiers.md — below this the OS is sold under its own floor
STALE_DAYS = 45       # untouched this long and the relationship is not real
SEVERITY = {"low": 1, "normal": 2, "high": 3}

# Named, pre-agreed risk classes. A closed vocabulary so the same risk is called the same
# thing across deals — free-text risks cannot be counted, and an uncountable pre-mortem
# teaches nothing on the second engagement.
RISK_KINDS = {
    "under-floor":   "priced below the OS floor — margin-negative once run cost lands",
    "no-decider":    "no decision-maker identified — a champion without authority",
    "scope-drift":   "the ask has changed materially since discovery",
    "no-data":       "they cannot or will not share the data the build needs",
    "single-thread": "one contact, no second relationship — the deal dies if they leave",
    "wrong-job":     "they are hiring us for something the OS does not actually do",
    "capacity":      "we could not deliver this on the timeline we would be promising",
    "unpaid-audit":  "they refused the paid diagnostic — the strongest known bad-fit signal",
}


def _d(iso):
    try:
        return datetime.date.fromisoformat(str(iso)[:10])
    except Exception:
        return None


def _age(iso):
    d = _d(iso)
    return (TODAY - d).days if d else None


def flags_for(deal, co, data, mirror_rows, contacts):
    """Every case AGAINST this deal, each citing its evidence. Never speculative."""
    out = []
    retainer = float(deal.get("retainer") or 0)
    if retainer and retainer < CORE_FLOOR:
        out.append({"kind": "under-floor", "severity": "high",
                    "evidence": f"retainer ${retainer:,.0f}/mo vs the ${CORE_FLOOR:,} Core floor",
                    "note": ("yourco absorbs the model spend, so a sub-floor retainer is not a "
                             "thin margin — it can be a negative one.")})

    people = [p for p in contacts if p.get("companyId") == (co or {}).get("id")]
    deciders = [p for p in people if p.get("role") in ("decision-maker", "co-decision-maker")]
    if people and not deciders:
        out.append({"kind": "no-decider", "severity": "high",
                    "evidence": f"{len(people)} contact(s) on this company, none marked a decision-maker",
                    "note": "A champion who cannot say yes cannot be sold to; they can only be briefed."})
    if len(people) == 1:
        out.append({"kind": "single-thread", "severity": "normal",
                    "evidence": f"one contact ({people[0].get('name')}), no second relationship",
                    "note": "The deal and the account both end if this person leaves or goes quiet."})

    age = _age(deal.get("lastTouch") or deal.get("stageSince"))
    if age is not None and age >= STALE_DAYS and deal.get("stage") not in ("parked", "pre-convo"):
        out.append({"kind": "stale", "severity": "normal",
                    "evidence": f"{age} days since the last touch, at stage {deal.get('stage')}",
                    "note": "Advanced on our board, dormant in reality — the stage is a claim nobody has tested."})

    m = next((r for r in mirror_rows if r.get("dealId") == deal.get("id")), None)
    if m and m.get("overreach"):
        out.append({"kind": "overreach", "severity": "high",
                    "evidence": f"our stage assumes {len(m['overreach'])} uncleared buyer step(s): "
                                + ", ".join(m["overreach"]),
                    "note": "We are further along than they are. That gap is where deals die."})
    if m and m.get("unmapped"):
        out.append({"kind": "our-gap", "severity": "low",
                    "evidence": "no buyer ladder filled in",
                    "note": "This is OUR omission, not a mark against them — fill the mirror before judging."})

    for r in (deal.get("churnHypothesis") or {}).get("risks", []) or []:
        k = r.get("key")
        out.append({"kind": k, "severity": r.get("severity") or "normal",
                    "evidence": "recorded pre-signature by " + ((deal.get("churnHypothesis") or {}).get("by") or "?"),
                    "note": r.get("note") or RISK_KINDS.get(k, "")})
    return out


def compute(data=None):
    if data is None:
        with open(DATA) as f:
            data = json.load(f)
    cos = {c["id"]: c for c in data.get("companies", []) or []}
    contacts = data.get("contacts") or []

    mirror_rows = []
    try:
        sys.path.insert(0, HERE)
        import mirror
        mirror_rows = mirror.compute(data).get("rows") or []
    except Exception:
        pass

    rows = []
    for d in (data.get("deals") or []):
        if d.get("stage") in ("parked", "live"):
            continue
        co = cos.get(d.get("companyId"))
        fl = flags_for(d, co, data, mirror_rows, contacts)
        # `our-gap` flags never count against the deal — they count against us.
        against = [f for f in fl if f["kind"] != "our-gap"]
        score = sum(SEVERITY.get(f["severity"], 2) for f in against)
        rows.append({
            "dealId": d.get("id"), "company": (co or {}).get("name") or d.get("name"),
            "stage": d.get("stage"), "retainer": float(d.get("retainer") or 0),
            "flags": fl, "againstCount": len(against), "score": score,
            "hasHypothesis": bool(d.get("churnHypothesis")),
            "verdict": ("decline — the case against is strong and specific" if score >= 6 else
                        "qualify harder before advancing" if score >= 3 else
                        "no recorded case against"),
        })
    rows.sort(key=lambda r: (-r["score"], -r["retainer"]))

    decline = [r for r in rows if r["score"] >= 6]
    harder = [r for r in rows if 3 <= r["score"] < 6]
    # Deals close to signature with no pre-mortem on file — the gate this module exists to hold.
    missing_pm = [r for r in rows if r["stage"] in ("demo-proposal", "signed-onboarding")
                  and not r["hasHypothesis"]]

    return {
        "generated": TODAY.isoformat(), "riskKinds": RISK_KINDS, "coreFloor": CORE_FLOOR,
        "rows": rows, "declineCount": len(decline), "qualifyCount": len(harder),
        "missingPremortem": missing_pm,
        "reading": (f"{len(decline)} deal(s) with a strong recorded case against, "
                    f"{len(harder)} needing harder qualification, "
                    f"{len(missing_pm)} at or past Demo and Proposal with no churn hypothesis on file."),
        "honesty": ("Nothing here declines a deal. It assembles the case against, from recorded "
                    "evidence only, and hands it to the Founder — walking away from revenue is his call. "
                    "Flags marked `our-gap` are omissions on yourco's side and are excluded from "
                    "the score; an unfilled mirror is not evidence about a buyer."),
    }


def main():
    r = compute()
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); return
    print("The anti-pipeline — the case against, per open deal\n")
    print("  " + r["reading"] + "\n")
    shown = [x for x in r["rows"] if x["flags"]]
    if not shown:
        print("  No open deal has a recorded case against it.")
    for row in shown[:14]:
        print(f"  {row['company'][:32]:<32} {row['stage']:<15} score {row['score']:<3} {row['verdict']}")
        for f in row["flags"]:
            mark = "·" if f["kind"] != "our-gap" else "○"
            print(f"      {mark} {f['kind']} ({f['severity']}) — {f['evidence']}")
    if r["missingPremortem"]:
        print(f"\n  ⚠ No churn hypothesis recorded on {len(r['missingPremortem'])} deal(s) at or past "
              f"Demo and Proposal:")
        for m in r["missingPremortem"]:
            print(f"      · {m['company']} ({m['stage']})")
        print("      A risk named before signature is a test. Named after, it is a rationalisation.")
    print(f"\n  {r['honesty']}")


if __name__ == "__main__":
    main()
