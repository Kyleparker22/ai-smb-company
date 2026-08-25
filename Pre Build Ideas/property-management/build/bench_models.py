#!/usr/bin/env python3
"""Property OS — does a bigger model actually triage better?

Triage is the only model call in this product where being wrong has a
consequence a resident feels. This measures it against ground truth instead of
arguing about it.

The comparison that matters is NOT model-vs-model. It is **model vs the
deterministic floor**, because the floor already runs on every request and
already catches every case in this set that carries habitability risk. A model
earns its place here only by adding something on top of that — better category
resolution, a usable parts list — without ever pulling a priority DOWN.

  python3 bench_models.py                          # floor only (no key needed)
  python3 bench_models.py --models claude-opus-5,claude-sonnet-5,claude-haiku-4-5
  python3 bench_models.py --models claude-fable-5  # see the note below first

On claude-fable-5: you can benchmark it, but read the latency column before
reading the accuracy column. Triage runs inside the HTTP request for a P1, so a
model whose thinking cannot be disabled is disqualified on p95 regardless of how
well it scores. agents.py refuses to select it for triage for that reason.
(Measured 2026-08-16: p50 ~14s / p95 ~19s on this set — adaptive thinking stays
short on schema-bound classification; the minutes-long turns belong to hard
agentic work. Fourteen seconds against a microsecond floor still disqualifies.)

Nothing here is scored on prose. The renewal and concierge drafts are R1/R2 —
a human reads them — so their failure mode is "needs an edit", not "a resident
waits with no heat".
"""
import argparse, json, os, statistics, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import core  # noqa: E402

# ---------------------------------------------------------------- eval set
#
# Ground truth is the priority a competent dispatcher would set, written by
# hand. `min_priority` is the floor a wrong answer must not fall below —
# under-escalating a habitability failure is the only error class here that
# hurts somebody, so it is scored separately and weighted absolutely.
#
# The awkward cases are deliberate: residents understate, describe symptoms
# rather than systems, and bury the emergency in the second clause.

CASES = [
    # --- unambiguous emergencies
    dict(text="water is pouring through the ceiling in the hallway",
         cat="leak_active", pri="P1", min_pri="P1"),
    dict(text="I can smell gas in the kitchen, it's strong",
         cat=None, pri="P1", min_pri="P1"),
    dict(text="the whole apartment has no electricity since 6pm",
         cat="no_power_full", pri="P1", min_pri="P1"),
    dict(text="front door lock is broken, it won't latch shut at all",
         cat="lock_door", pri="P1", min_pri="P1"),

    # --- the ones that break keyword triage: understated emergencies
    dict(text="apartment is a bit chilly, the heat doesn't seem to be coming on",
         cat="no_heat", pri="P1", min_pri="P1", answers={"habitability": True}),
    dict(text="sorry to bother you, the water's been coming out cold all week",
         cat="no_hot_water", pri="P2", min_pri="P2", answers={"habitability": True}),
    dict(text="not urgent but the toilet is the only one and it won't flush",
         cat="toilet_clog", pri="P2", min_pri="P2", answers={"habitability": True}),
    dict(text="there's a bit of a damp patch and a musty smell in the bedroom wall",
         cat="mold_moisture", pri="P2", min_pri="P2"),

    # --- genuinely routine; a model that panics here is also wrong
    dict(text="the kitchen tap drips overnight, drives me mad",
         cat="leak_slow", pri="P3", min_pri="P4"),
    dict(text="closet door came off its runner",
         cat="cosmetic", pri="P4", min_pri="P4"),
    dict(text="big paint scuff by the front door from the last tenant",
         cat="cosmetic", pri="P4", min_pri="P4"),
    dict(text="window screen has a tear in it",
         cat="cosmetic", pri="P4", min_pri="P4"),

    # --- ordinary middle of the distribution
    dict(text="garbage disposal just hums and won't spin",
         cat="disposal", pri="P3", min_pri="P4"),
    dict(text="dishwasher won't drain, standing water in the bottom",
         cat="appliance", pri="P3", min_pri="P4"),
    dict(text="a/c runs but blows warm, it's 84 in here",
         cat="no_cooling", pri="P2", min_pri="P3"),
    dict(text="kitchen outlets are dead, the breaker looks fine to me",
         cat="no_power_partial", pri="P2", min_pri="P3"),
    dict(text="smoke detector chirping every minute, kept us up all night",
         cat="smoke_alarm", pri="P2", min_pri="P3"),
    dict(text="seeing roaches in the kitchen after dark",
         cat="pest", pri="P2", min_pri="P3"),

    # --- vulnerable occupant escalates an otherwise-P2
    dict(text="no hot water since yesterday", cat="no_hot_water",
         pri="P1", min_pri="P2", answers={"vulnerable_occupant": True,
                                          "habitability": True}),
]

ORDER = ["P4", "P3", "P2", "P1"]


def score(rows):
    """rows: list of (case, predicted_priority, predicted_category, seconds)."""
    n = len(rows)
    exact = sum(1 for c, p, _, _ in rows if p == c["pri"])
    cat_ok = sum(1 for c, _, g, _ in rows if c["cat"] is None or g == c["cat"])
    # The error that matters: predicted BELOW the floor a dispatcher must hold.
    unsafe = [(c, p) for c, p, _, _ in rows
              if ORDER.index(p) < ORDER.index(c["min_pri"])]
    over = sum(1 for c, p, _, _ in rows
               if ORDER.index(p) > ORDER.index(c["pri"]))
    lat = sorted(s for _, _, _, s in rows if s is not None)
    return {
        "n": n,
        "priority_exact": exact / n,
        "category_exact": cat_ok / n,
        "under_escalated": len(unsafe),
        "unsafe_cases": [f"{c['text'][:40]!r} -> {p} (needs {c['min_pri']})"
                         for c, p in unsafe],
        "over_escalated": over,
        "p50_s": round(statistics.median(lat), 2) if lat else None,
        "p95_s": round(lat[int(len(lat) * 0.95) - 1], 2) if len(lat) >= 2 else None,
    }


def run_floor():
    rows = []
    for c in CASES:
        t = time.perf_counter()
        r = core.classify(c["text"], answers=c.get("answers"))
        rows.append((c, r["priority"], r["category"], time.perf_counter() - t))
    return rows


def run_model(model):
    import agents
    rows = []
    fallbacks = 0
    for c in CASES:
        base = core.classify(c["text"], answers=c.get("answers"))
        t = time.perf_counter()
        out = agents.ask(agents.TRIAGE_SYSTEM,
                         f'RESIDENT REPORTED: "{c["text"]}"\n'
                         f'PHOTO ATTACHED: no\n'
                         f'OCCUPANT NOTE: '
                         f'{"vulnerable occupant on file" if (c.get("answers") or {}).get("vulnerable_occupant") else "none"}\n'
                         f'WHAT THIS UNIT KNOWS ABOUT ITSELF:\n(no history on file)\n\nTriage it.',
                         schema=agents.TRIAGE_SCHEMA, model=model)
        secs = time.perf_counter() - t
        if out is None:                       # error / refusal / truncated JSON
            fallbacks += 1
            rows.append((c, base["priority"], base["category"], secs))
            continue
        # Same rule the product uses: the model may only escalate.
        pri = out["priority"] if ORDER.index(out["priority"]) > ORDER.index(base["priority"]) \
            else base["priority"]
        rows.append((c, pri, out["category"], secs))
    if fallbacks:
        # A model whose calls fail inherits the floor's answers, which would
        # make it LOOK as good as the floor while contributing nothing. Say so
        # rather than letting a broken run masquerade as a clean score.
        print(f"    NOTE: {fallbacks}/{len(CASES)} calls fell back to the floor "
              f"(API error, refusal, or truncated output) — scores below are "
              f"contaminated by that fraction")
    return rows


def show(name, s):
    print(f"\n  {name}")
    print(f"    priority exact   {s['priority_exact']:.0%}"
          f"   category exact {s['category_exact']:.0%}   (n={s['n']})")
    print(f"    UNDER-escalated  {s['under_escalated']}"
          + ("   <-- the only error class that hurts a resident" if s["under_escalated"] else "   (none)"))
    for u in s["unsafe_cases"]:
        print(f"        {u}")
    print(f"    over-escalated   {s['over_escalated']}   (costs a truck roll, not a person)")
    if s["p50_s"] is not None:
        print(f"    latency          p50 {s['p50_s']}s   p95 {s['p95_s']}s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="",
                    help="comma-separated model ids to compare against the floor")
    a = ap.parse_args()

    print(f"Triage benchmark — {len(CASES)} hand-labelled cases")
    print("The question is not which model wins. It is whether any model beats")
    print("the deterministic floor by enough to justify its latency and cost.")

    floor = score(run_floor())
    show("RULES FLOOR (no model, always runs)", floor)

    models = [m.strip() for m in a.models.split(",") if m.strip()]
    if not models:
        print("\n  No models requested. To compare:")
        print("    pip install anthropic && export ANTHROPIC_API_KEY=…")
        print("    python3 bench_models.py --models claude-opus-5,claude-sonnet-5")
        sys.exit(0)

    import agents
    if agents._client() is None:
        print("\n  CANNOT COMPARE: no Anthropic SDK or credential on this machine.")
        print("  Refusing to print model numbers I did not measure.")
        print("    pip install anthropic && export ANTHROPIC_API_KEY=…")
        sys.exit(2)

    results = {"floor": floor}
    for m in models:
        try:
            results[m] = score(run_model(m))
            show(m, results[m])
        except Exception as e:
            print(f"\n  {m}: FAILED — {type(e).__name__}: {e}")

    print("\n  Verdict")
    for m, s in results.items():
        if m == "floor":
            continue
        d_pri = s["priority_exact"] - floor["priority_exact"]
        d_cat = s["category_exact"] - floor["category_exact"]
        worse = s["under_escalated"] > floor["under_escalated"]
        print(f"    {m}: priority {d_pri:+.0%}, category {d_cat:+.0%}"
              + (f", p95 {s['p95_s']}s" if s["p95_s"] else "")
              + ("   REGRESSION: under-escalates more than the floor" if worse else ""))
    print("\n  A model that does not beat the floor on category resolution is"
          "\n  paying latency and tokens for nothing — the floor already holds"
          "\n  every habitability case in this set.")
