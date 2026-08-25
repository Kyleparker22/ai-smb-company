#!/usr/bin/env python3
"""The decision P&L — grading `decisions/` against what happened next.

Every serious company keeps a decision log. **None of them ever grade it.** Decisions get
written, filed, and never revisited except as archaeology — so the same company makes the
same class of mistake repeatedly while holding a perfect written record of having done so.

yourco can grade them, for one structural reason: `decisions/`, the CRM, and git history
live in ONE repository. Each decision carries a date; the ghost pipeline already reconstructs
the exact board state on any past date (crm/ghost.py). So for every decision you can ask what
the pipeline did in the window before it and the window after, and put the two side by side.

WHAT THIS IS NOT. It is not causal. Nothing here proves a decision *caused* a change — a
pipeline moves for a hundred reasons and a solo founder makes several decisions a week. The
output is deliberately phrased as "what followed", never "what resulted", and every row
carries the confounder count: how many OTHER decisions landed inside the same window. A
decision competing with six others for credit is credited to none of them.

REFUSAL RULES:
  · A decision needs WINDOW days of board history on BOTH sides. Anything closer to the
    edges of the git record than that is reported as `unmeasurable`, not as zero effect.
  · Below MIN_MOVES stage transitions in a window, the window is `too quiet` — a pipeline
    that barely moved cannot distinguish a good decision from a dormant month.
  · No decision is ever ranked "best" or "worst". The output is evidence for a human review;
    ranking noise would manufacture false confidence in exactly the direction that feels good.

Run:
    python3 crm/decision_pl.py
    python3 crm/decision_pl.py --json
    python3 crm/decision_pl.py --top 15
"""
import json, os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
REPO = os.path.dirname(HERE)
DATA = os.path.join(DATA_DIR, "data.json")
DECISIONS = os.path.join(REPO, "decisions")
TODAY = datetime.date.today()

WINDOW = 21        # days either side of a decision
MIN_MOVES = 2      # stage transitions in a window before it is read at all

DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def _d(iso):
    try:
        return datetime.date.fromisoformat(str(iso)[:10])
    except Exception:
        return None


def decisions():
    """Every decision, dated from its filename (the house convention: YYYY-MM-DD_slug.md)."""
    out = []
    if not os.path.isdir(DECISIONS):
        return out
    for fn in sorted(os.listdir(DECISIONS)):
        if not fn.endswith(".md") or fn.startswith("_"):
            continue
        m = DATE_RE.match(fn)
        if not m:
            continue
        d = _d(m.group(0))
        if not d:
            continue
        title = fn[11:-3].replace("-", " ")
        try:
            head = open(os.path.join(DECISIONS, fn), encoding="utf-8").read(400)
            first = next((l.strip("# ").strip() for l in head.splitlines() if l.startswith("# ")), "")
            if first:
                title = first
        except Exception:
            pass
        out.append({"file": fn, "date": d, "title": title})
    return out


def transitions(timeline):
    """Every stage MOVE in the reconstructed board history: (date, dealId, from, to)."""
    moves = []
    prev = None
    for snap in timeline:
        cur = snap.get("stages") or {}
        d = _d(snap.get("date"))
        if prev is not None and d:
            for did, st in cur.items():
                was = prev.get(did)
                if was is not None and was != st:
                    moves.append({"date": d, "dealId": did, "from": was, "to": st})
                elif was is None:
                    moves.append({"date": d, "dealId": did, "from": None, "to": st})
        prev = cur
    return moves


def _window(moves, lo, hi, order):
    """Movement inside [lo, hi): count, and net rungs travelled (forward minus backward)."""
    inw = [m for m in moves if lo <= m["date"] < hi]
    net = 0
    for m in inw:
        if m["from"] is None:
            continue
        try:
            net += order.index(m["to"]) - order.index(m["from"])
        except ValueError:
            pass
    return {"moves": len(inw), "netRungs": net,
            "deals": sorted({m["dealId"] for m in inw})}


def compute(top=None):
    with open(DATA) as f:
        data = json.load(f)
    try:
        sys.path.insert(0, HERE)
        import ghost
        g = ghost.compute()
    except Exception as e:
        return {"generated": TODAY.isoformat(), "status": "no history",
                "why": f"the ghost timeline is unavailable ({type(e).__name__}: {e}); "
                       f"without reconstructed board states there is nothing to compare against."}

    timeline = g.get("timeline") or []
    order = g.get("order") or [s["key"] for s in data.get("stages", [])]
    if len(timeline) < 2:
        return {"generated": TODAY.isoformat(), "status": "no history",
                "why": "fewer than two board states on record — nothing to compare."}

    span_lo = _d(timeline[0]["date"])
    span_hi = _d(timeline[-1]["date"])
    moves = transitions(timeline)
    decs = decisions()

    rows, unmeasurable = [], []
    for dec in decs:
        d = dec["date"]
        if d - datetime.timedelta(days=WINDOW) < span_lo or d + datetime.timedelta(days=WINDOW) > span_hi:
            unmeasurable.append({**dec, "date": d.isoformat(),
                                 "why": f"needs {WINDOW}d of board history either side; the record "
                                        f"runs {span_lo} → {span_hi}"})
            continue
        before = _window(moves, d - datetime.timedelta(days=WINDOW), d, order)
        after = _window(moves, d, d + datetime.timedelta(days=WINDOW), order)
        confounders = [x["file"] for x in decs
                       if x is not dec and d <= x["date"] < d + datetime.timedelta(days=WINDOW)]
        row = {**dec, "date": d.isoformat(), "before": before, "after": after,
               "confounders": len(confounders), "confounderFiles": confounders[:6]}
        if before["moves"] + after["moves"] < MIN_MOVES:
            row["status"] = "too quiet"
            row["reading"] = (f"{before['moves'] + after['moves']} stage move(s) in the whole "
                              f"{WINDOW*2}-day window — a board this still cannot distinguish a "
                              f"good decision from a dormant month.")
        else:
            row["status"] = "measured"
            dm = after["moves"] - before["moves"]
            dr = after["netRungs"] - before["netRungs"]
            row["deltaMoves"], row["deltaRungs"] = dm, dr
            row["reading"] = (
                f"{before['moves']}→{after['moves']} moves, net rungs {before['netRungs']}→"
                f"{after['netRungs']}. "
                + ("Attributed to nothing — "
                   f"{row['confounders']} other decisions landed in the same window."
                   if row["confounders"] >= 3 else
                   "What FOLLOWED this decision, not what it caused."))
        rows.append(row)

    measured = [r for r in rows if r["status"] == "measured"]

    # ---- decision DENSITY: the finding that outranks every individual row ---------------
    # If more decisions land inside a window than the board makes moves, no decision can be
    # isolated from its neighbours and the whole exercise degrades to noise. That is not a
    # defect in the method — it is a real, measurable fact about how the company operates,
    # and it is more actionable than any single row: it says the decision log is being used
    # as a diary rather than as a set of separable bets.
    attributable = [r for r in measured if r["confounders"] < 3]
    density = None
    if measured:
        avg_conf = sum(r["confounders"] for r in measured) / len(measured)
        density = {
            "avgConfounders": round(avg_conf, 1),
            "attributable": len(attributable), "of": len(measured),
            "reading": (
                f"{len(attributable)} of {len(measured)} measurable decisions can be attributed to "
                f"anything at all. On average **{avg_conf:.0f} other decisions land in the same "
                f"21-day window**, against {len(moves)} stage moves across the entire "
                f"{(span_hi - span_lo).days}-day record. "
                + ("At this density no decision is separable from its neighbours, and no honest "
                   "P&L can be drawn. That is the finding: decisions are being logged at roughly "
                   "one a day while the board moves a handful of times a month, so the log reads "
                   "as a diary rather than a set of separable bets. Fewer, larger, spaced-out "
                   "decisions would become measurable ones."
                   if avg_conf >= 3 else
                   "Density is low enough that individual rows carry some signal.")),
        }
    rows.sort(key=lambda r: r["date"], reverse=True)
    if top:
        rows = rows[:int(top)]

    return {
        "generated": TODAY.isoformat(), "window": WINDOW, "minMoves": MIN_MOVES,
        "status": "measured" if measured else "insufficient",
        "spanFrom": span_lo.isoformat(), "spanTo": span_hi.isoformat(),
        "decisions": len(decs), "measured": len(measured),
        "unmeasurable": unmeasurable, "boardMoves": len(moves),
        "rows": rows, "density": density, "attributable": len(attributable),
        "honesty": ("This is correlation over a 21-day window on a board with very little "
                    "movement, on a company with zero closed deals. It says what FOLLOWED a "
                    "decision and never what a decision caused. Rows where 3+ other decisions "
                    "landed in the same window are explicitly attributed to nothing. Nothing here "
                    "ranks decisions as good or bad — that judgement is the Founder's, and this is the "
                    "evidence he would otherwise be recalling from memory."),
    }


def main():
    top = None
    if "--top" in sys.argv:
        try:
            top = int(sys.argv[sys.argv.index("--top") + 1])
        except Exception:
            pass
    r = compute(top)
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); return
    if r.get("status") == "no history":
        print("Decision P&L — " + r["why"]); return
    print(f"Decision P&L — {r['decisions']} decision(s), {r['measured']} measurable "
          f"(board history {r['spanFrom']} → {r['spanTo']}, {r['boardMoves']} stage moves)\n")
    if r.get("density"):
        print(f"  ⚠ {r['density']['reading']}\n")
    for row in r["rows"]:
        if row["status"] != "measured":
            continue
        arrow = "↑" if row.get("deltaMoves", 0) > 0 else ("↓" if row.get("deltaMoves", 0) < 0 else "→")
        print(f"  {row['date']}  {arrow} {row['title'][:62]}")
        print(f"      {row['reading']}")
    quiet = [r2 for r2 in r["rows"] if r2["status"] == "too quiet"]
    if quiet:
        print(f"\n  {len(quiet)} decision(s) sit in windows too quiet to read.")
    if r["unmeasurable"]:
        print(f"  {len(r['unmeasurable'])} fall outside the board record entirely.")
    print(f"\n  {r['honesty']}")


if __name__ == "__main__":
    main()
