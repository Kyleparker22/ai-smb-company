#!/usr/bin/env python3
"""yourco — the connector's ghost: what their book would be worth if YOURCO had moved at its own pace.

Every referral dashboard in the world exists to grade the partner. This one grades **yourco**.

A connector hands over an introduction and then has no way of knowing whether it stalled because the
business wasn't interested or because yourco sat on it for three weeks. That asymmetry is the whole
reason referral programs are distrusted, and it is invisible by construction — the vendor owns the
only record. So: reconstruct where each of their referrals *would* be today if yourco had moved it at
**yourco's own median velocity**, and show the connector the difference, in their own commission.

Nothing here is a second computation. `ghost.compute()` already reconstructs board history from git
and derives per-stage medians with a refusal rule (`MIN_OBS`: below 3 completed occupancies a rung is
not "measured" and any deal whose path crosses it gets a POSITION but no dollar figure). This module
**filters those rows to one connector and re-denominates the gap into their commission** — it never
re-derives a median, and it inherits every refusal.

Three honesty rules this module holds, and the copy on the console states all three:
  1. **A gap is not a debt.** The figure is what the book would be worth on yourco's own averages —
     expected value, not money the connector was owed. It is never presented as a balance.
  2. **Unpriced stays unpriced.** If a referral's path crosses a rung yourco has not measured, the
     connector sees the ghost POSITION and an explicit "we can't put a number on this" — never an
     invented one.
  3. **It reports yourco being FAST too.** `aheadOfPace` is rendered with the same prominence as
     behind. A ledger that only surfaces the vendor's failures when they flatter the partner is just
     a different flavour of marketing.

Usage:
  python3 crm/connector_ghost.py                 # every connector (operator view)
  python3 crm/connector_ghost.py "Sample Contact"    # one connector
  from connector_ghost import compute
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
CRM = os.path.join(DATA_DIR, "data.json")
sys.path.insert(0, HERE)
from connector_statements import books, _tier, tier_input   # the book + the rate, never re-derived

# Below this many of the connector's own referrals we show the per-referral detail but refuse to
# state a book-level total: one referral behind pace is an anecdote, not a pattern, and a headline
# number computed off it would read as a claim about yourco's reliability that the sample can't carry.
MIN_REFERRALS_FOR_TOTAL = 3


def _ghost_rows(ghost_data=None):
    """yourco's own ghost board. Injectable so tests never shell out to git."""
    if ghost_data is not None:
        return ghost_data
    try:
        import ghost
        return ghost.compute()
    except Exception as e:                       # git unavailable, no history, cache unwritable…
        return {"ghost": [], "unavailable": str(e), "measuredRungs": 0, "totalRungs": 0}


def compute(name, d=None, ghost_data=None):
    """One connector's ghost. Returns None if they are not a connector in yourco's records.

    Shape:
      {"rows": [...], "behind": n, "ahead": n, "priced": n, "unpriced": n,
       "commissionGap": float|None, "rate": pct, "enough": bool, "why": str}
    `commissionGap` is None whenever it cannot be defended — too few referrals, no priced rows, or
    yourco's own history unavailable. None means "we will not say"; it never means zero.
    """
    d = d if d is not None else json.load(open(CRM))
    connectors, _credits, _dl = books(d)
    if name not in connectors:
        return None
    book = connectors[name]
    _tn, rate = _tier(tier_input(book, d.get("meta", {}).get("referralTiers") or {}),
                      (d.get("meta") or {}).get("referralTiers") or {})

    mine = {r["companyId"] for r in book["active"] + book["inactive"]}
    by_company_id = {c["id"]: c for c in d.get("companies", [])}
    g = _ghost_rows(ghost_data)
    deal_company = {x["id"]: x.get("companyId") for x in d.get("deals", [])}

    rows, priced_gap, n_priced, n_unpriced, behind, ahead = [], 0.0, 0, 0, 0, 0
    for r in g.get("ghost", []):
        cid = deal_company.get(r.get("id"))
        if cid not in mine:
            continue                              # never another connector's book
        # Re-denominate: yourco's EV gap on the deal becomes THIS connector's commission on it.
        # `priced` is inherited, not recomputed — if yourco won't price it, neither will we.
        gap = (float(r["evGap"]) * rate / 100.0) if (r.get("priced") and r.get("evGap") is not None) else None
        if gap is None:
            n_unpriced += 1
        else:
            n_priced += 1
            priced_gap += gap
        if r.get("rungsBehind"):
            behind += 1
        elif r.get("rungsAhead"):
            ahead += 1
        rows.append({
            "company": (by_company_id.get(cid) or {}).get("name") or r.get("company"),
            "companyId": cid,
            "real": r.get("real"), "ghost": r.get("ghost"),
            "rungsBehind": r.get("rungsBehind") or 0, "rungsAhead": r.get("rungsAhead") or 0,
            "daysBehind": r.get("daysBehind"),
            "priced": bool(r.get("priced")),
            "commissionGap": round(gap, 2) if gap is not None else None,
            "unpricedRungs": r.get("unpricedRungs") or [],
            "explain": r.get("explain") or "",
        })
    rows.sort(key=lambda x: (-(x["rungsBehind"]), -(x["commissionGap"] or 0)))

    # The refusal. Three separate reasons, each said in its own words — "no number" that doesn't say
    # WHY is indistinguishable from "zero", and the two mean opposite things.
    if g.get("unavailable"):
        enough, why = False, ("yourco cannot read its own board history right now, so it cannot say "
                              "what its normal pace is. No figure is shown rather than a guessed one.")
    elif not rows:
        enough, why = False, "No referrals of yours are on the board yet — nothing to compare."
    elif len(rows) < MIN_REFERRALS_FOR_TOTAL:
        enough, why = False, (f"Only {len(rows)} of your referrals are on the board. One or two is an "
                              f"anecdote, not a pattern — the per-referral detail is shown, but no "
                              f"book-level figure until there are {MIN_REFERRALS_FOR_TOTAL}.")
    elif not n_priced:
        enough, why = False, ("yourco has not run enough deals through these stages to have a "
                              "measured pace for them. Positions are shown; the cost is left "
                              "unclaimed rather than invented.")
    else:
        enough, why = True, (f"Computed from {n_priced} of your {len(rows)} referrals — the ones whose "
                             f"whole path crosses stages yourco has actually measured."
                             + (f" {n_unpriced} more are shown without a figure." if n_unpriced else ""))

    return {"connector": name, "rows": rows, "rate": rate,
            "behind": behind, "ahead": ahead, "priced": n_priced, "unpriced": n_unpriced,
            "commissionGap": round(priced_gap, 2) if enough else None,
            "enough": enough, "why": why,
            "measuredRungs": g.get("measuredRungs"), "totalRungs": g.get("totalRungs")}


def main():
    d = json.load(open(CRM))
    connectors, _c, _dl = books(d)
    who = [sys.argv[1]] if len(sys.argv) > 1 else sorted(connectors)
    if not who:
        print("No connectors with referred companies yet (program pre-launch).")
        return
    for name in who:
        r = compute(name, d)
        if r is None:
            print(f"{name!r} is not a connector with a book in yourco's records.")
            continue
        head = (f"${r['commissionGap']:,.2f}" if r["commissionGap"] is not None else "— (not stated)")
        print(f"\n# {name} — yourco's pace against its own median")
        print(f"  book-level gap: {head} · {r['behind']} behind pace · {r['ahead']} ahead · rate {r['rate']}%")
        print(f"  {r['why']}")
        for x in r["rows"]:
            g = f"${x['commissionGap']:,.2f}" if x["commissionGap"] is not None else "no figure"
            print(f"    {x['company']:<34} {x['real']} → ghost {x['ghost']}  ({g})")


if __name__ == "__main__":
    main()
