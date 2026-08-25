#!/usr/bin/env python3
"""Twin Test — feasibility / minimum-detectable-effect calculator.

The refusal mechanic from offerings/twin-test/SPEC.md §7, as a working tool:
given a client's real baseline rate and inbound volume, compute the smallest
true effect a randomized test could honestly detect within the allowed
duration — and refuse (verdict REFUSE) any test whose question is smaller
than that. Deterministic stdlib math only; no LLM anywhere in this path.

Statistics: two-proportion z-test, normal approximation, two-sided alpha,
solved for the detectable absolute difference by bisection. Unequal splits
supported. Both alpha and power are printed on every readout, per spec.
"""

import argparse
import sys
from statistics import NormalDist

_N = NormalDist()

WORKED_EXAMPLE = """\
worked example (obviously illustrative numbers, not client data):
  A made-up shop closes 25% of leads and gets 40 leads/week. Owner wants to
  test a new quote script for up to 8 weeks, 50/50 split, and would care
  about a 5-point swing (25% -> 30%):

    python3 mde_calc.py --baseline 0.25 --weekly-volume 40 --max-weeks 8 \\
        --split 0.5 --mme-points 5

  -> n = 160 per arm; MDE ~ 14.6 points at alpha=0.05, power=0.8.
     14.6 > 5, so the verdict is REFUSE: at this volume, 8 weeks can only
     honestly detect a ~15-point swing; a "result" about a 5-point question
     would be noise wearing a costume. The tool then reports what WOULD be
     answerable: the effect size this volume can detect, and the weeks
     needed (often impractically many -- that honesty is the product).
"""


def power_two_prop(p1: float, delta: float, n1: float, n2: float, alpha: float) -> float:
    """Approximate power to detect p2 = p1 + delta (two-sided), unequal n."""
    p2 = p1 + delta
    if not (0.0 < p2 < 1.0):
        return 1.0 if delta > 0 else 0.0
    z_a = _N.inv_cdf(1.0 - alpha / 2.0)
    pbar = (n1 * p1 + n2 * p2) / (n1 + n2)
    se0 = (pbar * (1.0 - pbar) * (1.0 / n1 + 1.0 / n2)) ** 0.5
    se1 = (p1 * (1.0 - p1) / n1 + p2 * (1.0 - p2) / n2) ** 0.5
    if se1 == 0.0:
        return 1.0
    # dominant tail only; the neglected tail is vanishingly small at these z's
    return _N.cdf((abs(delta) - z_a * se0) / se1)


def mde(p1: float, n1: float, n2: float, alpha: float, target_power: float) -> float:
    """Smallest absolute uplift delta with power >= target, by bisection."""
    lo, hi = 1e-9, 1.0 - p1 - 1e-9
    if power_two_prop(p1, hi, n1, n2, alpha) < target_power:
        return float("inf")  # not detectable even at ceiling
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if power_two_prop(p1, mid, n1, n2, alpha) >= target_power:
            hi = mid
        else:
            lo = mid
    return hi


def weeks_needed(p1, weekly, split, alpha, power_t, target_delta, cap=520):
    """Smallest whole weeks T such that MDE at T <= target_delta (None if > cap)."""
    for t in range(1, cap + 1):
        n1 = weekly * t * split
        n2 = weekly * t * (1.0 - split)
        if n1 < 1 or n2 < 1:
            continue
        if mde(p1, n1, n2, alpha, power_t) <= target_delta:
            return t
    return None


def parse_rate(x: float, name: str) -> float:
    """Accept 0.25 or 25 (percent) for convenience."""
    r = x / 100.0 if x > 1.0 else x
    if not (0.0 < r < 1.0):
        sys.exit(f"error: {name} must be a rate in (0,1) or a percent in (0,100); got {x}")
    return r


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="mde_calc.py",
        description=__doc__,
        epilog=WORKED_EXAMPLE,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--baseline", type=float, required=True,
                    help="baseline conversion rate: 0.25 or 25 (percent). From the client's real trailing data (Leak Meter taps), never a guess.")
    ap.add_argument("--weekly-volume", type=float, required=True,
                    help="inbound leads/week for the tested segment")
    ap.add_argument("--split", type=float, default=0.5,
                    help="share of inbound randomized to the treatment arm (default 0.5)")
    ap.add_argument("--max-weeks", type=int, required=True,
                    help="max acceptable test duration in weeks (from the brief)")
    ap.add_argument("--alpha", type=float, default=0.05,
                    help="two-sided significance level (default 0.05)")
    ap.add_argument("--power", type=float, default=0.8,
                    help="target power (default 0.8)")
    ap.add_argument("--mme-points", type=float, default=None,
                    help="client's minimum meaningful effect, in absolute percentage points (e.g. 5 = a 5-point swing). Elicited in dollars first, converted. Optional: omit to just see the MDE.")
    a = ap.parse_args()

    p1 = parse_rate(a.baseline, "--baseline")
    if not (0.0 < a.split < 1.0):
        sys.exit("error: --split must be strictly between 0 and 1")
    if a.weekly_volume <= 0 or a.max_weeks <= 0:
        sys.exit("error: --weekly-volume and --max-weeks must be positive")
    if not (0.0 < a.alpha < 1.0 and 0.5 < a.power < 1.0):
        sys.exit("error: need 0<alpha<1 and 0.5<power<1")

    n_t = a.weekly_volume * a.max_weeks * a.split
    n_c = a.weekly_volume * a.max_weeks * (1.0 - a.split)
    d = mde(p1, n_c, n_t, a.alpha, a.power)

    print("Twin Test feasibility check  (alpha=%g two-sided, power=%g -- both apply to any readout)" % (a.alpha, a.power))
    print(f"  baseline rate : {p1:.1%}   volume: {a.weekly_volume:g}/wk   split: {1-a.split:.0%} control / {a.split:.0%} treatment")
    print(f"  at max {a.max_weeks} weeks : n = {n_c:.0f} control + {n_t:.0f} treatment")
    if d == float("inf"):
        print("  MDE           : not detectable at any effect size with this sample. REFUSE.")
        return
    print(f"  MDE           : {d*100:.1f} points absolute ({p1:.1%} -> {p1+d:.1%}, a {d/p1:.0%} relative change)")
    print()
    print(f"  This volume can honestly answer questions about effects >= {d*100:.1f} points.")
    print("  Smaller than that, a readout would be a lie -- confident noise, not a result.")

    if a.mme_points is None:
        print("\n  (No --mme-points given: showing the MDE only. The run/refuse verdict needs")
        print("   the client's minimum meaningful effect from the signed experiment brief.)")
        return

    mme = a.mme_points / 100.0
    print(f"\n  Client's minimum meaningful effect: {a.mme_points:.1f} points.")
    if d <= mme:
        print(f"  VERDICT: RUN. MDE {d*100:.1f} <= {a.mme_points:.1f} points within {a.max_weeks} weeks.")
        print("  Next step: the signed experiment brief (pre-registered metric, decision rule,")
        print("  harm stop-rule) -- nothing runs unsigned.")
    else:
        print(f"  VERDICT: REFUSE. At this volume, {a.max_weeks} weeks can only detect a")
        print(f"  {d*100:.1f}-point swing; the question asked is about {a.mme_points:.1f} points.")
        print("  Running it anyway would produce a confident answer the data cannot support.")
        t = weeks_needed(p1, a.weekly_volume, a.split, a.alpha, a.power, mme)
        print("  Honest alternatives:")
        if t is not None:
            print(f"    - run longer: ~{t} weeks reaches an MDE of {a.mme_points:.1f} points")
        else:
            print("    - run longer: even 10 years would not get there at this volume")
        print(f"    - test a bolder change (one you'd expect to move >= {d*100:.1f} points)")
        print("    - grow volume first, then test (the feasibility check is free; re-run anytime)")


if __name__ == "__main__":
    main()
