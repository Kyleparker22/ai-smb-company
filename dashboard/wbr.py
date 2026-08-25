#!/usr/bin/env python3
"""WBR — the Amazon weekly-business-review discipline, applied to yourco.

Three ideas from Amazon's WBR, and they work together:

1. **Controllable inputs, above the outputs.** HQ's nine goal metrics are all *outputs* — MRR,
   live clients, deals in motion. the Founder cannot move any of them on a Tuesday. He can move
   conversations held, deliverables shipped, companies touched, deals advanced. Outputs are the
   score; inputs are the game, and a dashboard that shows only the score is a vanity surface no
   matter how honest each number is.
2. **The 6-12 chart.** Trailing six weeks beside trailing twelve months, same metric, same place.
   The mechanism is not the metric count — it is that the layout never changes, so an anomaly
   announces itself instead of having to be hunted.
3. **Format lock.** The point of an unchanging deck is that the eye already knows where everything
   sits. So this module's output order is FIXED and does not sort by interestingness.

WHERE THE NUMBERS COME FROM, AND WHAT ISN'T THERE
Inputs are counted from `crm/data.json`'s activity log and deal `stageSince` — things the OS
observes as a side effect of the work, never typed into a goals file. Two inputs the Founder would
obviously want remain **not computable** and are listed as such rather than estimated: new
prospects added (companies carry no created date) and warm intros made. Naming them is the useful
part — each is one CRM field away.

**Referral asks used to be the third.** The CRM recorded `Referral` (one arrived) but nothing
recorded the *ask*, so the connector program's leading indicator was structurally unknowable
rather than merely unmeasured. A `Referral ask` activity type was added 2026-08-13; asks are now
counted here, and `referral_conversion()` reports asks→referrals — refusing a rate below five
asks, because a percentage off a handful is noise with a percent sign on it.

The 6-12 series runs on `timemachine.as_of()`, so a historical number and today's number come from
one implementation. **A flat line at zero is reported as flat at zero**; pre-revenue, most of these
series carry no information and the module says so rather than drawing a confident line through
nothing.

Read-only. GET /api/wbr.
"""
import os, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

CRM = os.path.join(ROOT, "crm", "data.json")

# FORMAT LOCK: this order is fixed. Do not re-sort by value, recency or interestingness — the
# whole mechanism is that the reader's eye learns the positions.
INPUTS = [
    ("conversationsHeld", "Conversations held", "Meeting or Call logged",
     "the only input that creates pipeline; everything else downstream of it is optional"),
    ("deliverablesShipped", "Deliverables shipped", "activity of type Deliverable",
     "give-first proof landing in a prospect's hands"),
    ("companiesTouched", "Companies touched", "distinct company with any activity",
     "breadth of contact — catches a week spent entirely on one account"),
    ("dealsAdvanced", "Deals advanced", "deal whose stage changed",
     "movement, as opposed to activity that leaves the board where it was"),
    ("warmIntrosMade", "Warm intros made", "activity of type 'Warm intro made'",
     "the give-first half of the warm network — introducing two people who should know each "
     "other, which is what earns the right to ask later"),
    ("referralAsks", "Referral asks made", "activity of type 'Referral ask'",
     "the connector program's leading indicator — the one input that creates referrals, and "
     "the only one on this list that is asked for rather than delivered"),
    ("newProspectsAdded", "New prospects added", "company with createdAt in the window",
     "top-of-funnel replenishment — the input that stops the board shrinking"),
    ("nextActionsSet", "Next actions set", "activity carrying a nextAction",
     "whether the week ended with the board ready to be worked"),
]

# Emptied 2026-08-13: all three named gaps were closed by adding two activity types and one
# company field. The list stays in the payload rather than being deleted — the NEXT gap belongs
# here, and a structure that only exists while it has contents tends not to come back.
NOT_COMPUTABLE = []

# createdAtSource vocabulary, named ONCE because the reader and the writers had already drifted.
# Every intake path (promote, promote_intent, site_intake, snapshot_intake, instantly_sync) stamps
# "recorded". Nothing in the codebase writes "manual-entry" — the 16 companies carrying it were
# stamped in a single bulk edit on 2026-08-23, all with the same date, which makes that date exactly
# as inferred as a git-recovered one. So the rule is a DENY-list on inference, not an allow-list on
# one string: anything not known to be inferred counts, and a new intake path gets counted the day
# it ships without anyone remembering to add it here.
INFERRED_SOURCES = {"git-first-appearance", "manual-entry"}


def observed_companies(crm):
    """Companies whose createdAt was seen at creation, not reconstructed afterwards."""
    return [c for c in (crm.get("companies") or [])
            if c.get("createdAtSource") and c["createdAtSource"] not in INFERRED_SOURCES]

# The output metrics that get a 6-12 series. Fixed order, same reason.
SERIES = ["pipelineValue", "dealsInMotion", "mrr", "companies", "contacts"]

WEEKS_BACK = 6
MONTHS_BACK = 12


def _new_prospect_gap():
    """`New prospects added` reads 0 two ways, and they mean opposite things.

    Every company in the CRM today carries an INFERRED creation date — 25 recovered from git, 16
    bulk-stamped on one day. So the metric is structurally 0 no matter what happened that week, and
    a reader cannot tell "you added nobody" from "nothing here can answer that". This was listed as
    not-computable until 2026-08-13, when adding a `createdAt` field closed the gap on paper — the
    field arrived, an observed VALUE never did. Reported as a gap again, computed rather than
    hardcoded, so it disappears by itself the first time a real intake path writes one.
    """
    try:
        if observed_companies(_load(CRM) or {}):
            return []
    except Exception:
        return []
    return [{"metric": "New prospects added",
             "why": "every company's createdAt is inferred (git-recovered or bulk-stamped), so this "
                    "counts 0 regardless of the week — that is a missing input, not a quiet week",
             "fix": "it self-clears the first time an intake path writes a company (all five stamp "
                    "createdAtSource='recorded'); until then, read the 0 as 'unknown'"}]


def _load(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _week_start(d):
    return d - datetime.timedelta(days=d.weekday())


def count_inputs(start, end, crm=None):
    """Inputs observed in [start, end). Counted from the activity log, never typed."""
    crm = crm or _load(CRM) or {}
    acts = [a for a in (crm.get("activities") or [])
            if a.get("date") and start.isoformat() <= a["date"] < end.isoformat()]
    deals = [d for d in (crm.get("deals") or [])
             if d.get("stageSince") and start.isoformat() <= d["stageSince"] < end.isoformat()]
    return {
        "conversationsHeld": sum(1 for a in acts if (a.get("type") or "") in ("Meeting", "Call")),
        "deliverablesShipped": sum(1 for a in acts if (a.get("type") or "") == "Deliverable"),
        "companiesTouched": len({a.get("companyId") for a in acts if a.get("companyId")}),
        "dealsAdvanced": len(deals),
        "warmIntrosMade": sum(1 for a in acts if (a.get("type") or "") == "Warm intro made"),
        "referralAsks": sum(1 for a in acts if (a.get("type") or "") == "Referral ask"),
        # only dates OBSERVED at creation count as new-in-window. The 25 companies backfilled
        # from git carry createdAtSource="git-first-appearance"; counting those would put a
        # spike of "new prospects" in whatever week the repo happened to record them.
        "newProspectsAdded": sum(
            1 for c in observed_companies(crm)
            if start.isoformat() <= str(c.get("createdAt") or "") < end.isoformat()),
        "nextActionsSet": sum(1 for a in acts if (a.get("nextAction") or "").strip()),
    }


def referral_conversion(crm=None):
    """Asks -> referrals. The pair exists so this ratio is computable; before the 'Referral ask'
    type was added (2026-08-13) only the lagging half was recorded, so the connector program's
    conversion was structurally unknowable rather than merely unknown.

    Refuses a rate below MIN_ASKS: a conversion computed from two asks is noise with a
    percent sign on it."""
    MIN_ASKS = 5
    crm = crm or _load(CRM) or {}
    acts = crm.get("activities") or []
    asks = sum(1 for a in acts if (a.get("type") or "") == "Referral ask")
    got = sum(1 for a in acts if (a.get("type") or "") == "Referral")
    rate = round(got / asks * 100) if asks >= MIN_ASKS else None
    return {
        "asks": asks, "referrals": got, "ratePct": rate, "floor": MIN_ASKS,
        "refusal": (None if rate is not None else
                    f"{asks} ask(s) recorded — no conversion rate below {MIN_ASKS}. "
                    f"A percentage off a handful of asks is noise with a percent sign on it."),
        "note": ("'Referral ask' is the leading half and 'Referral' the lagging half. Logging "
                 "the ask whether or not it lands is the whole point — asks are countable "
                 "before any referral exists."),
    }


def inputs_block(today=None):
    today = today or datetime.date.today()
    this_start = _week_start(today)
    weeks = []
    for i in range(WEEKS_BACK):
        s = this_start - datetime.timedelta(weeks=i)
        weeks.append({"weekOf": s.isoformat(), "counts": count_inputs(s, s + datetime.timedelta(weeks=1))})
    weeks.reverse()

    rows = []
    for key, label, source, why in INPUTS:
        series = [w["counts"][key] for w in weeks]
        prior = series[:-1]
        rows.append({
            "metric": key, "label": label, "source": source, "why": why,
            "thisWeek": series[-1],
            "series": series,
            "priorAvg": round(sum(prior) / len(prior), 1) if prior else None,
            "allZero": not any(series),
        })
    live = [r for r in rows if not r["allZero"]]
    return {
        "weekOf": this_start.isoformat(),
        "weeks": [w["weekOf"] for w in weeks],
        "rows": rows,
        "notComputable": NOT_COMPUTABLE + _new_prospect_gap(),
        "referralConversion": referral_conversion(),
        "allQuiet": not live,
        "note": ("Controllable inputs — things the Founder can move on a Tuesday. Counted from the CRM's "
                 "activity log and deal stage changes, never typed into a goals file. Outputs are "
                 "the score; these are the game. Order is FIXED (format lock): an unchanging "
                 "layout is what lets an anomaly announce itself."),
        "zeroNote": ("Every input is zero across all six weeks. That is a real reading of the "
                     "week, not a broken panel.") if not live else None,
    }


def series_block(today=None):
    """The 6-12: trailing six weeks and trailing twelve months, same metric, same place."""
    today = today or datetime.date.today()
    try:
        import timemachine as tm
    except Exception as e:
        return {"error": f"time machine unavailable: {type(e).__name__}: {e}", "rows": []}

    labels = {m["key"]: (m["label"], m["unit"]) for m in
              [{"key": k, "label": l, "unit": u} for k, l, u in tm.METRICS]}

    def at(d):
        snap = tm.as_of(d.isoformat())
        return (snap or {}).get("metrics") or {}

    week_dates = [_week_start(today) - datetime.timedelta(weeks=i) for i in range(WEEKS_BACK)][::-1]
    month_dates = []
    y, m = today.year, today.month
    for _ in range(MONTHS_BACK):
        month_dates.append(datetime.date(y, m, 1))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    month_dates.reverse()

    wsnap = {d: at(d) for d in week_dates}
    msnap = {d: at(d) for d in month_dates}

    rows = []
    for key in SERIES:
        label, unit = labels.get(key, (key, ""))
        w = [wsnap[d].get(key) for d in week_dates]
        mo = [msnap[d].get(key) for d in month_dates]
        known = [v for v in (w + mo) if isinstance(v, (int, float))]
        flat = bool(known) and len(set(known)) == 1
        rows.append({
            "metric": key, "label": label, "unit": unit,
            "weeks": [{"on": d.isoformat(), "v": wsnap[d].get(key)} for d in week_dates],
            "months": [{"on": d.isoformat(), "v": msnap[d].get(key)} for d in month_dates],
            "flat": flat,
            "flatNote": (f"unchanged at {known[0]} across every point — this series carries no "
                         f"information yet, which is a fact about the business and not about "
                         f"the chart") if flat else None,
            "current": w[-1] if w else None,
        })
    informative = sum(1 for r in rows if not r["flat"])
    return {
        "weekDates": [d.isoformat() for d in week_dates],
        "monthDates": [d.isoformat() for d in month_dates],
        "rows": rows,
        "informative": informative,
        "note": ("Trailing six weeks beside trailing twelve months, same metric, same position, "
                 "every week. Computed through timemachine.as_of(), so a historical number and "
                 "today's number are one implementation. A flat series is labelled flat rather "
                 "than drawn as if it were a trend."),
        "honestLimit": (f"{len(rows) - informative} of {len(rows)} series are flat. Pre-revenue "
                        f"that is expected; this panel earns its keep the week revenue starts."),
    }


def build(today=None):
    today = today or datetime.date.today()
    return {
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "today": today.isoformat(),
        "inputs": inputs_block(today),
        "series": series_block(today),
        "formatLock": ("Row order is fixed and never sorted by value or interestingness. The "
                       "unchanging layout IS the mechanism — it is how Amazon reviews 400+ "
                       "metrics in an hour."),
    }


if __name__ == "__main__":
    d = build()
    i, s = d["inputs"], d["series"]
    print(f"WBR — week of {i['weekOf']}\n")
    print("CONTROLLABLE INPUTS (the game)")
    for r in i["rows"]:
        spark = " ".join(str(x) for x in r["series"])
        print(f"  {r['label']:<22} this wk {r['thisWeek']:<4} prior avg {r['priorAvg']}   [{spark}]")
        print(f"      {r['why']}")
    if i["zeroNote"]:
        print("  " + i["zeroNote"])
    print("\n  NOT COMPUTABLE (named, not estimated):")
    for n in i["notComputable"]:
        print(f"    · {n['metric']} — {n['why']}  -> {n['fix']}")
    print(f"\n6-12 SERIES (the score)")
    if s.get("error"):
        print("  " + s["error"])
    else:
        for r in s["rows"]:
            w = " ".join("—" if x["v"] is None else str(x["v"]) for x in r["weeks"])
            m = " ".join("—" if x["v"] is None else str(x["v"]) for x in r["months"])
            print(f"  {r['label']:<20} 6wk [{w}]   12mo [{m}]" + ("   FLAT" if r["flat"] else ""))
        print("  " + s["honestLimit"])
