#!/usr/bin/env python3
"""The loss autopsy — why a deal died, diagnosed rather than labelled.

Every CRM records `outcome: lost` with a free-text reason. That is a label, not a diagnosis,
and it fails at exactly the question that matters: **who actually beat us?**

Christensen's point is that the competitor is almost never a rival vendor. It is "do
nothing", "have Colton figure it out", "hire a $45k coordinator". Those demand opposite
responses — losing to inertia means the pain was never made explicit; losing to a rival
means it was, and we lost on the merits; losing on price means the value was understood and
judged insufficient. Treating all three as "lost" throws away the only lesson available.

The diagnosis costs no new data collection. **The mirror board already knows which rung of
the buyer's own ladder they never cleared** (crm/mirror.py), and that rung is the cause of
death. A buyer who never cleared `budget` did not choose a competitor; they never got to a
decision at all.

CAUSE OF DEATH is derived from the FIRST unclear rung, cross-checked against price events
and the recorded reason. Where those disagree, the autopsy says so rather than picking —
a contradiction between what we wrote down and what the buyer's ladder shows is itself the
most interesting finding in the file.

REFUSAL RULES:
  · A deal with no mirror data gets `unmapped`, never a guessed cause. Inferring the buyer's
    ladder from our own stage would delete the entire point of the second column.
  · Patterns across losses need MIN_LOSSES; below that it reports each autopsy individually
    and claims nothing about where deals "tend" to die.
  · It never blames the buyer. Every cause is written as something yourco did or failed to
    establish, because that is the only half we control.

Run:
    python3 crm/autopsy.py
    python3 crm/autopsy.py --json
"""
import json, os, sys, datetime
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
DATA = os.path.join(DATA_DIR, "data.json")
TODAY = datetime.date.today()

MIN_LOSSES = 4      # before any cross-loss pattern is claimed

# The buyer's ladder, in order (mirrors STEPS in crm/mirror.py — change one, change both).
STEPS = ["felt", "internal", "budget", "risk", "story", "authority", "switch"]

# Which rung failed -> what actually beat us, phrased as OUR failure.
CAUSE = {
    "felt":      ("qualification", "They never said the problem out loud in their own words. "
                                   "We were selling to a need we identified, not one they had."),
    "internal":  ("qualification", "Nobody else inside their world had heard them say it. A pain "
                                   "one person holds privately does not survive a budget cycle."),
    "budget":    ("inertia",       "They could not name the line this gets paid from. This is the "
                                   "classic no-decision loss — nobody chose a rival, they simply "
                                   "never reached a decision."),
    "risk":      ("inertia",       "Their personal downside was never priced. An unanswered "
                                   "'what happens to ME if this fails' stalls at the last step, "
                                   "every time, and it stalls silently."),
    "story":     ("translation",   "They had no sentence to explain this to their team. We sold "
                                   "them, and left them unable to sell it onward."),
    "authority": ("access",        "Someone who could say no was never in the room — briefed, not "
                                   "present. We ran the whole deal past the wrong person."),
    "switch":    ("imagination",   "They could not picture a normal Monday once it was running. "
                                   "It never became real to them, so it never became urgent."),
}
CLEARED_ALL = ("merits", "They cleared every rung on their own ladder and still said no. This is "
                         "the honest loss — the value was understood and judged insufficient. "
                         "Look at price and at the offer, not at the process.")


def _d(iso):
    try:
        return datetime.date.fromisoformat(str(iso)[:10])
    except Exception:
        return None


def mirror_of(h):
    """The buyer-ladder state for a holder. Prefers the snapshot taken at close — the live
    mirror can drift after the fact, and an autopsy must read the body as it was found."""
    snap = (h.get("mirrorAtClose") or {}).get("steps")
    if snap:
        return snap, "snapshot at close"
    st = (h.get("mirror") or {}).get("steps")
    if st:
        return st, "live mirror (no close snapshot — may have drifted since)"
    return None, None


def _status(st, k):
    v = st.get(k)
    return str(v.get("status") if isinstance(v, dict) else v)


def autopsy_one(h, cos):
    co = cos.get(h.get("companyId"), {})
    st, src = mirror_of(h)
    row = {
        "dealId": h.get("id"), "company": co.get("name") or h.get("name"),
        "closedDate": h.get("closedDate"), "why": (h.get("why") or h.get("lostReason") or "").strip(),
        "value": float(h.get("value") or 0) or float(h.get("retainer") or 0) * 12,
        "mirrorSource": src,
    }
    if not st:
        row.update({"cause": "unmapped", "causeLabel": "unmapped",
                    "diagnosis": ("No buyer ladder was ever filled in for this deal, so there is "
                                  "nothing to autopsy. The cause of death is unrecoverable — fill "
                                  "the mirror while a deal is alive, not after."),
                    "firstGap": None, "cleared": [], "contradiction": None})
        return row

    cleared = [k for k in STEPS if _status(st, k) == "yes"]
    first_gap = next((k for k in STEPS if _status(st, k) != "yes"), None)
    row["cleared"] = cleared
    row["firstGap"] = first_gap
    if first_gap is None:
        row["cause"], row["diagnosis"] = CLEARED_ALL
        row["causeLabel"] = "lost on the merits"
    else:
        row["cause"], row["diagnosis"] = CAUSE[first_gap]
        row["causeLabel"] = first_gap

    # ---- cross-check the recorded reason against the ladder ----------------------------
    # A stated reason that contradicts the evidence is the most useful line in this file:
    # it is where the story we told ourselves and the story the record tells diverge.
    w = row["why"].lower()
    said_price = any(t in w for t in ("price", "expensive", "cost", "budget", "afford", "cheap"))
    said_rival = any(t in w for t in ("competitor", "went with", "chose ", "another vendor", "someone else"))
    contradiction = None
    if said_rival and row["cause"] == "inertia":
        contradiction = ("Recorded as lost to a competitor, but they never cleared "
                         f"`{first_gap}` — a buyer who cannot name their budget line does not "
                         "run a vendor selection. This was probably a no-decision dressed up "
                         "as a bake-off, and it was likely lost long before the competitor appeared.")
    elif said_price and first_gap in ("felt", "internal"):
        contradiction = ("Recorded as a price loss, but they never established the problem was "
                         "real to them. 'Too expensive' against an unfelt problem means the value "
                         "was never built, not that the number was wrong. Cutting price here "
                         "would fix nothing and cost margin.")
    elif not row["why"]:
        contradiction = "No reason was recorded at all — David's hygiene rule requires one."
    row["contradiction"] = contradiction
    return row


def compute(data=None):
    if data is None:
        with open(DATA) as f:
            data = json.load(f)
    cos = {c["id"]: c for c in data.get("companies", []) or []}
    lost = [h for h in (data.get("closed") or []) if h.get("outcome") == "lost"]
    rows = [autopsy_one(h, cos) for h in lost]
    rows.sort(key=lambda r: -(r["value"] or 0))

    mapped = [r for r in rows if r["cause"] != "unmapped"]
    out = {
        "generated": TODAY.isoformat(), "steps": STEPS, "causes": CAUSE,
        "losses": len(rows), "mapped": len(mapped), "unmapped": len(rows) - len(mapped),
        "rows": rows, "minLosses": MIN_LOSSES,
        "openMirrorGaps": [
            {"dealId": d.get("id"), "company": cos.get(d.get("companyId"), {}).get("name") or d.get("name"),
             "stage": d.get("stage")}
            for d in (data.get("deals") or [])
            if d.get("stage") not in ("pre-convo", "parked") and not ((d.get("mirror") or {}).get("steps"))
        ],
    }

    if len(mapped) < MIN_LOSSES:
        out.update({
            "status": "insufficient", "needs": MIN_LOSSES - len(mapped), "pattern": None,
            "reading": (f"{len(mapped)} autopsied loss(es). {MIN_LOSSES - len(mapped)} more before "
                        f"this claims where deals TEND to die. Each autopsy below still stands on "
                        f"its own — one loss is a fact, four is a pattern."),
        })
        return out

    by_cause = Counter(r["cause"] for r in mapped)
    by_rung = Counter(r["firstGap"] for r in mapped if r["firstGap"])
    lost_value = {}
    for r in mapped:
        lost_value[r["cause"]] = lost_value.get(r["cause"], 0) + (r["value"] or 0)
    top_cause, top_n = by_cause.most_common(1)[0]
    out.update({
        "status": "measured",
        "pattern": {
            "byCause": dict(by_cause), "byRung": dict(by_rung), "valueByCause": lost_value,
            "topCause": top_cause,
            "reading": (f"{top_n} of {len(mapped)} losses died of **{top_cause}** — "
                        f"${lost_value.get(top_cause,0):,.0f} of annualized value. "
                        + ("Inertia is the leading cause, which means the work is upstream: "
                           "the problem is not being made explicit and personal early enough."
                           if top_cause == "inertia" else
                           "This is a qualification problem, not a closing problem — the deals "
                           "should not have advanced."
                           if top_cause == "qualification" else
                           "These reached a real decision and lost it. Look at the offer.")),
        },
        "reading": f"{len(mapped)} autopsied · leading cause: {top_cause}",
    })
    return out


def main():
    r = compute()
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); return
    print(f"Loss autopsy — {r['losses']} loss(es), {r['mapped']} with a buyer ladder to read\n")
    if not r["rows"]:
        print("  Nothing has been lost yet, so there is nothing to autopsy.")
        print("  This becomes useful the first time a deal closes lost — and it is only useful")
        print("  then if the mirror was filled in WHILE the deal was alive.")
        if r["openMirrorGaps"]:
            print(f"\n  ⚠ {len(r['openMirrorGaps'])} live deal(s) past Pre Convo have no mirror at all:")
            for g in r["openMirrorGaps"][:10]:
                print(f"    · {g['company']} ({g['stage']})")
            print("  Fill these now. A ladder reconstructed after the loss is a story, not evidence.")
        return
    if r["status"] == "measured":
        print("  " + r["pattern"]["reading"] + "\n")
    else:
        print("  " + r["reading"] + "\n")
    for row in r["rows"]:
        print(f"  {row['company'][:30]:<30} {row['causeLabel']:<14} ${row['value']:,.0f}")
        print(f"      {row['diagnosis']}")
        if row.get("contradiction"):
            print(f"      ⚠ {row['contradiction']}")


if __name__ == "__main__":
    main()
