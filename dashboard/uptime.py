#!/usr/bin/env python3
"""yourco — runtime availability, computed from beats that are missing.

The last genuinely unmeasured thing on the 2026-08-25 metric sweep that was nobody else's blocker.
Kemba owned *runtime uptime (%)* and **nothing in the repo measured availability** — which was also
precondition #1 of the client SLA (`processes/contracts/sla.md` §7), whose own §6 says an unmeasured
month reads as a **miss**. So the absence of this file was a standing failure, not a gap.

THE IDEA, AND IT IS THE WHOLE DESIGN. A log records what happened while the box was working, so a
log can never record an outage. `runtime/heartbeat.sh` instead writes one line every 15 minutes and
nothing else, and this module computes

    uptime = beats RECEIVED / beats EXPECTED over the window

so **a missing line is the outage**. Absence is the measurement, not a hole in it — the same lesson
`learnings/ops/2026-08-07_absence-is-invisible-to-this-os` cost the OS three dark days to learn.

FOUR REFUSALS, AND EACH ONE IS A LIE THIS WOULD OTHERWISE TELL
1. **It will not claim uptime for time before monitoring existed.** The window is clipped to the
   first beat ever recorded. The most tempting first reading of any monitor is "100%, all-time", and
   it is always false: nothing was watching.
2. **It will not compute a percentage off a handful of beats.** Below `MIN_EXPECTED` there is no
   number, because 99.5% and 97% are three beats apart at that resolution.
3. **Paused is not down.** A deliberate stand-down (`runtime/.paused`) is the runtime *available and
   idle*. Reported as a separate `serving` figure so a planned pause can never read as an outage,
   and an outage can never hide behind "we meant to".
4. **A gap at the tail may be sync lag, not downtime**, and it says so. Beats reach the repo when a
   loop commits or when the heartbeat's own 6-hourly push fires, so the newest data is at most that
   stale. Reporting a fresh tail-gap as an outage would manufacture incidents.

WHAT IT MEASURES, PRECISELY. *The runtime working* — not the box having power. A host that is up
while every unit is dead is not "up" in any sense that matters to an agent. That is also what keeps
this from duplicating Atlas's number: **Atlas measures whether the work landed** (artifacts inside
cadence), **this measures whether the substrate was able to run at all**, sampled on a clock that
does not care whether anything was scheduled. Loop liveness at 59% cannot tell you whether the box
was down or the loops were failing; together these two can.

Read-only. GET /api/uptime · CLI: `python3 dashboard/uptime.py [days]`
"""
import os, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
ROOT = os.environ.get("YOURCO_DATA_ROOT") or REPO

STORE = os.path.join(ROOT, "loops", "_health", "heartbeat.jsonl")
INTERVAL_MIN = 15          # MUST match runtime/heartbeat.sh and yourco-heartbeat.timer
WINDOW_DAYS = 7
MIN_EXPECTED = 24          # 6 hours of beats before any percentage is stated
SYNC_LAG_MIN = 6 * 60 + INTERVAL_MIN   # the heartbeat's own push cadence, plus one beat
SLA_TARGET = 99.5          # processes/contracts/sla.md §2 — quoted, never restated as our own


def _parse(ts):
    try:
        return datetime.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def read_beats():
    """-> (beats, bad). A malformed line is COUNTED, never silently dropped: a store that quietly
    loses rows understates uptime and looks like an outage."""
    if not os.path.exists(STORE):
        return [], 0
    beats, bad = [], 0
    try:
        with open(STORE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    b = json.loads(line)
                except ValueError:
                    bad += 1
                    continue
                t = _parse(b.get("ts"))
                if t is None:
                    bad += 1
                    continue
                b["_t"] = t
                beats.append(b)
    except OSError:
        return [], 0
    beats.sort(key=lambda b: b["_t"])
    return beats, bad


def _gaps(beats, step):
    """Contiguous runs of missing beats, as (from, to, missed)."""
    out = []
    for a, b in zip(beats, beats[1:]):
        delta = (b["_t"] - a["_t"]).total_seconds()
        missed = int(round(delta / step)) - 1
        if missed >= 1:
            out.append((a["_t"], b["_t"], missed))
    out.sort(key=lambda g: -g[2])
    return out


def compute(days=WINDOW_DAYS, now=None):
    beats, bad = read_beats()
    now = now or datetime.datetime.now(datetime.timezone.utc)
    step = INTERVAL_MIN * 60

    if not beats:
        return {"state": "unmeasured", "value": None,
                "refusal": ("no heartbeat has ever been recorded. runtime/heartbeat.sh + "
                            "yourco-heartbeat.timer exist in the repo; the timer is a HOST install "
                            "and only the Founder can enable it — until then availability is unmeasured, "
                            "and under the SLA's own §6 an unmeasured month reads as a miss."),
                "beats": 0, "bad": bad, "installed": False}

    first, last = beats[0]["_t"], beats[-1]["_t"]
    window_start = max(now - datetime.timedelta(days=days), first)
    # Never claim uptime for time before anything was watching.
    clipped = window_start > (now - datetime.timedelta(days=days))
    inwin = [b for b in beats if window_start <= b["_t"] <= now]
    expected = int((now - window_start).total_seconds() // step)
    received = len(inwin)
    tail_min = (now - last).total_seconds() / 60.0

    if expected < MIN_EXPECTED:
        return {"state": "unmeasured", "value": None,
                "refusal": (f"only {expected} beat(s) expected since monitoring began "
                            f"({first.date()}). No percentage below {MIN_EXPECTED} — at a "
                            f"{INTERVAL_MIN}-minute beat, {SLA_TARGET}% and 97% are three beats "
                            f"apart."),
                "beats": received, "bad": bad, "installed": True,
                "firstBeat": first.isoformat(timespec="seconds"),
                "lastBeat": last.isoformat(timespec="seconds")}

    pct = min(100.0, received / expected * 100.0)
    serving = sum(1 for b in inwin if not b.get("paused"))
    paused = received - serving
    gaps = _gaps(inwin, step)
    worst = gaps[0] if gaps else None
    failed_seen = max((int(b.get("failed_units") or 0) for b in inwin), default=0)

    notes = []
    if clipped:
        notes.append(f"window clipped to the first beat ({first.date()}) — nothing was watching "
                     f"before that, so no claim is made about it")
    if tail_min > SYNC_LAG_MIN:
        notes.append(f"newest beat is {tail_min / 60:.1f}h old, past the {SYNC_LAG_MIN / 60:.1f}h "
                     f"sync cadence — this is a real gap, not lag")
    elif tail_min > INTERVAL_MIN * 2:
        notes.append(f"newest beat is {tail_min:.0f}m old; beats reach the repo on a commit, so a "
                     f"tail gap under {SYNC_LAG_MIN / 60:.1f}h is sync lag, not an outage")
    if paused:
        notes.append(f"{paused} beat(s) were a deliberate pause — available and idle, not down")
    if failed_seen:
        notes.append(f"up to {failed_seen} yourco unit(s) in a failed state during the window — up "
                     f"is not the same as healthy")
    if bad:
        notes.append(f"{bad} unparseable line(s) in the store, counted rather than dropped")

    return {
        "state": "computed",
        "value": round(pct, 2),
        "servingPct": round(min(100.0, serving / expected * 100.0), 2),
        "expected": expected, "received": received, "paused": paused,
        "windowDays": days, "intervalMin": INTERVAL_MIN,
        "firstBeat": first.isoformat(timespec="seconds"),
        "lastBeat": last.isoformat(timespec="seconds"),
        "tailMinutes": round(tail_min),
        "gaps": [{"from": a.isoformat(timespec="seconds"), "to": b.isoformat(timespec="seconds"),
                  "missedBeats": n, "minutes": n * INTERVAL_MIN} for a, b, n in gaps[:5]],
        "longestGapMinutes": (worst[2] * INTERVAL_MIN) if worst else 0,
        "failedUnitsSeen": failed_seen, "bad": bad, "installed": True,
        "slaTarget": SLA_TARGET,
        "meetsSlaTarget": pct >= SLA_TARGET,
        "notes": notes,
    }


def runtime_uptime_pct():
    """The (value, unit, note) contract dashboard/northstar.py's METRICS table expects."""
    r = compute()
    if r["state"] != "computed":
        return None, "%", r["refusal"]
    note = f"{r['received']} of {r['expected']} expected beats over {r['windowDays']}d"
    if r["longestGapMinutes"]:
        note += f" · longest gap {r['longestGapMinutes']}m"
    if r["notes"]:
        note += " · " + "; ".join(r["notes"][:2])
    return r["value"], "%", note


# Same shape as loop_metrics / crm_metrics / client_metrics so northstar merges it identically —
# and so runtime/consistency-check.py, which reads these tables, can see it.
METRICS = {
    "runtimeUptimePct": runtime_uptime_pct,
}
MECHANISM = {
    "runtimeUptimePct": "heartbeat",
}


def build():
    r = compute()
    r["generated"] = datetime.datetime.now().isoformat(timespec="seconds")
    r["store"] = "loops/_health/heartbeat.jsonl"
    r["note"] = ("Uptime is beats received over beats expected — a missing line IS the outage. "
                 "Measures the runtime working, not the box having power. Atlas's loop liveness "
                 "measures whether the work landed; this measures whether the substrate could run "
                 "at all. Neither one alone can tell a dead box from dead loops.")
    r["slaNote"] = ("This is yourco's OWN runtime. processes/contracts/sla.md promises availability "
                    "of a CLIENT's OS, and there is no client deployment to measure — so SLA "
                    "precondition #1 is now half closed: the mechanism exists, its subject does not.")
    return r


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else WINDOW_DAYS
    r = compute(days)
    print("\n=== runtime availability ==================================================")
    if r["state"] != "computed":
        print("  UNMEASURED — " + r["refusal"])
        return 0
    print(f"  {r['value']}% over {r['windowDays']}d   ({r['received']} of {r['expected']} beats)")
    print(f"  serving (not paused): {r['servingPct']}%   ·   SLA reference {r['slaTarget']}% → "
          f"{'meets' if r['meetsSlaTarget'] else 'MISSES'}")
    print(f"  first beat {r['firstBeat']} · last {r['lastBeat']} ({r['tailMinutes']}m ago)")
    if r["gaps"]:
        print("  gaps:")
        for g in r["gaps"]:
            print(f"    {g['from']} → {g['to']}  ({g['minutes']}m, {g['missedBeats']} beats)")
    for n in r["notes"]:
        print("  ⚠ " + n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
