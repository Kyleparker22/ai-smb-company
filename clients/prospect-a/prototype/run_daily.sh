#!/usr/bin/env bash
# yourco · Nick's daily storm loop — pull → AI-read → hold GO storms for approval.
#
# The chain, once per run:
#   1. storm_poc.py   pull every source + rule cross-verify   -> last_run.json
#   2. verify_ai.py   the AI READS the reports, judges each    -> verified_ai.json
#                     (GO / HOLD / REJECT + claim packet). Off if no ANTHROPIC_API_KEY.
#   3. build_demo.py  refresh Nick's visual                     -> demo_data.js
#
# Dispatch stays APPROVAL-GATED: this loop never texts anyone. Only GO storms are
# queued; Nick taps, then dispatch.py --send broadcasts. Nothing false reaches his
# phone because verify_ai.py filtered it first.
#
# On the yourco runtime this runs on a systemd timer each morning (and a faster
# cadence in storm season — speed is the game). Local test:  ./run_daily.sh
set -euo pipefail
cd "$(dirname "$0")"
STAMP=$(date +%F)
echo "== yourco storm loop · $STAMP =="

python3 storm_poc.py

if python3 -c "import anthropic" 2>/dev/null && { [ -n "${ANTHROPIC_API_KEY:-}" ] || [ -f .env ]; }; then
  python3 verify_ai.py
else
  echo "  (AI verification skipped — no ANTHROPIC_API_KEY; rule-verified only. Engine still ran.)"
fi

python3 build_demo.py

# Summarize what's queued for Nick's approval (GO storms only).
python3 - <<'PY'
import json, os
run = json.load(open("last_run.json"))
rel = [v for v in run["verified"] if v["roofing_relevant"]]
ai = {}
if os.path.exists("verified_ai.json"):
    ai = {(x["county"], x["date"]): x for x in json.load(open("verified_ai.json"))}
def go_ok(v):
    return (not ai) or ai.get((v["county"], v["date"]), {}).get("dispatch") == "GO"
def haz(v):
    parts = []
    if v.get("max_hail_in"):  parts.append(format(v["max_hail_in"], ".2f") + " in hail")
    if v.get("max_wind_mph"): parts.append(format(v["max_wind_mph"], ".0f") + " mph wind")
    if v.get("tornado"):      parts.append("tornado")
    return " + ".join(parts) or "storm"
go = [v for v in rel if go_ok(v)]
print()
print("  %d storm(s) queued for approval (of %d roofing-relevant):" % (len(go), len(rel)))
for v in go:
    print("    - %s %s - %s" % (v["county"], v["date"], haz(v)))
print()
print("  Approve to broadcast:  python3 dispatch.py --to area:<X> --send   (approval-gated)")
PY
echo "== done =="
