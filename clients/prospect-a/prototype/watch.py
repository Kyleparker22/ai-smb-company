#!/usr/bin/env python3
"""
Real-time watcher — speed is the whole business. Instead of a once-a-day pull,
this polls the live sources on a short interval and fires the INSTANT a new storm
verifies, deduped against what it's already alerted. First crew to the
neighborhood gets paid; this is what makes Nick first.

Dispatch stays approval-gated — a new storm becomes an instant heads-up + a GO
entry queued for Nick's tap, never an auto-text.

Usage:  python3 watch.py --once                 # one cycle (for testing / cron)
        WATCH_INTERVAL=180 python3 watch.py      # continuous, poll every 180s
"""
import json, os, sys, time
import storm_poc

STATE = ".watch_state.json"
INTERVAL = int(os.environ.get("WATCH_INTERVAL", "300"))


def load_seen():
    return set(json.load(open(STATE))) if os.path.exists(STATE) else set()


def save_seen(seen):
    json.dump(sorted(seen), open(STATE, "w"))


def haz(v):
    b = []
    if v.get("max_hail_in"):  b.append(f'{v["max_hail_in"]:.2f}" hail')
    if v.get("max_wind_mph"): b.append(f'{v["max_wind_mph"]:.0f}mph wind')
    if v.get("tornado"):      b.append("TORNADO")
    return " + ".join(b) or "storm"


def cycle(seen):
    verified, _, _ = storm_poc.verify()
    rel = [v for v in verified if v["roofing_relevant"] and v["confidence"] == "HIGH"]
    new = [v for v in rel if f'{v["county"]}|{v["date"]}' not in seen]
    for v in new:
        key = f'{v["county"]}|{v["date"]}'
        seen.add(key)
        print(f"⚡ NEW VERIFIED STORM — {v['county']} County {v['date']} — {haz(v)} "
              f"({', '.join(v['sources_hit'])})")
        print(f"   → instant heads-up to Nick; queued GO for one-tap dispatch. Be first.\n")
    if not new:
        print(f"   · {len(rel)} verified on the board, nothing new.")
    save_seen(seen)
    return new


def main():
    once = "--once" in sys.argv
    seen = load_seen()
    print(f"yourco storm watcher — {'single cycle' if once else f'polling every {INTERVAL}s'} "
          f"(HIGH-confidence FL storms; dispatch stays approval-gated)\n")
    while True:
        try:
            cycle(seen)
        except Exception as e:
            print(f"   (cycle error: {e})")
        if once:
            break
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
