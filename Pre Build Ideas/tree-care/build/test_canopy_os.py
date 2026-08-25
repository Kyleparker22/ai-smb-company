#!/usr/bin/env python3
"""Canopy OS — the suite. `python3 test_canopy_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["CANOPYOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="canopyos_test_")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from datetime import timedelta

import agents, core, seed
from core import store
from _kit.store import iso, now

PASS = FAIL = 0


def ok(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {label}")


print("== seed ==")
seed.main()
ok(len(store.load("jobs")) >= 120, "jobs seeded")
ok(len(store.load("estimates")) == 70, "estimates seeded")

print("== triage: emergency reads first ==")
for text, want in (("a tree came down on the garage last night", "emergency"),
                   ("huge limb through the roof of my car", "emergency"),
                   ("there's a widow maker hanging over where the kids play", "emergency"),
                   ("tree across the road at the end of our street", "emergency"),
                   ("the elm snapped halfway up in the wind just now", "emergency"),
                   ("is my oak safe? it's leaning more than last year", "hazard_ask"),
                   ("should we worry about the dead maple by the fence", "hazard_ask"),
                   ("is that big branch over the house dangerous", "hazard_ask"),
                   ("how much to remove two trees in the backyard", "quote"),
                   ("need a price on stump grinding for three stumps", "quote"),
                   ("what day is the crew coming this week", "schedule"),
                   ("", "human"),
                   ("thanks, yard looks great", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:42]} → {want}")

print("== the emergency route ==")
out = agents.handle_message("ms_demo_storm")
step = out["steps"][0]
ok(step["action"] == "route_emergency", "emergency routed")
ok("911 first" in step["said"], "the ack says 911 first if anyone is trapped")
ok(any(e["kind"] == "route_emergency" for e in store.events()), "R2 route lands in the log")

print("== the hazard ask: no verdict, ever ==")
out = agents.handle_message("ms_demo_hazard")
step = out["steps"][0]
ok(step["action"] == "draft_assessment_visit", "arborist visit drafts")
body = step["draft"]
ok("arborist" in body.lower(), "the visit is the answer")
low = body.lower()
ok(" safe" not in low.replace("should answer it", "") and "hazardous" not in low
   and "dangerous" not in low,
   "neither verdict word in the reply")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "assert_tree_safety"
       for e in store.events()), "assert_tree_safety refused + logged")
ok("yourco" not in body.lower(), "white-label: no yourco name in outward copy")

print("== the power-line gate ==")
oks, why = core.can_schedule(store.by_id("jobs", "jb_demo_lines"))
ok(not oks and "no utility clearance" in why, "power-line job without clearance refused")
ok("fatality mechanism" in why, "the refusal names the stake")
r = agents.schedule_job("jb_demo_lines")
ok("refused" in r, "schedule_job refuses")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "schedule_powerline_unclear"
       for e in store.events()), "schedule_powerline_unclear logged")
r = agents.schedule_job("jb_demo_clear")
ok(r.get("rung") == "R1" and r.get("approval"), "clear job queues at R1")
oks, why = core.can_schedule({"near_powerlines": True, "utility_clearance_ref": "UC-1234"})
ok(oks and "UC-1234" in why, "cleared power-line job schedules, citing the reference")

print("== estimate ladder + copy ==")
e9 = {"id": "es_x", "customer_name": "Dana Mercer", "desc": "storm-split oak takedown",
      "amount": 3900, "sent_at": iso(now() - timedelta(days=10))}
store.upsert("estimates", e9)
ok(core.estimate_plan(e9)["action"] == "draft_chase", "an aged estimate is due a touch")
e9["touches"] = [{"at": iso(now() - timedelta(days=2))}]
ok(core.estimate_plan(e9)["action"] == "none", "6-day cooldown holds")
e9["touches"] = [{"at": iso(now() - timedelta(days=30 - i))} for i in range(3)]
ok("silence is an answer" in core.estimate_plan(e9)["why"], "ladder exhausts at 3")
b1 = agents._estimate_chase_copy(e9, 1)
ok("Dana" in b1 and "$3,900" in b1, "chase copy carries name and number")
b3 = agents._estimate_chase_copy(e9, 3)
ok("leave it with you" in b3, "touch 3 closes without pressure")
ok(not any(w in (b1 + b3).lower() for w in ("fall on", "kill", "destroy", "dangerous")),
   "no fear-selling in estimate copy")

print("== PHC + assessment copy ==")
p9 = {"id": "ph_x", "customer_name": "Osei", "program": "oak treatment",
      "next_due": iso(now() + timedelta(days=12))}
body = agents._phc_copy(p9)
ok("oak treatment" in body and "renew" in body.lower(), "PHC copy names the program")
qc = agents._quote_copy({"from": "Renner"})
ok("site look" in qc and "free" in qc, "quote reply routes to the site look")
ok("$" not in qc, "no number before the site look")

print("== matrix ==")
for a in ("assert_tree_safety", "schedule_powerline_unclear", "promise_no_damage"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("assert_tree_safety", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a_["action"] == "assert_tree_safety" and a_["state"] == "pending"
           for a_ in store.load("approvals")), "R0 never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no emergency missed")
ok("HOUSE" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("open_estimate_value" in r["recorded"], "estimate value recorded")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Estimates recovered by the ladder"]["value"] is None,
   "revenue line blank without the operator's close rate")
ok(labels["Storm-call answer speed"]["kind"] == "scenario", "the storm hour is a scenario")

print("== recovered, counted ==")
base = core.recovered_this_week()
e9["won_at"] = iso(now() - timedelta(days=1))
store.upsert("estimates", e9)
p9["renewed_at"] = iso(now())
store.upsert("phc", p9)
store.log_event("emergency_callback", "ms_demo_storm", "human:coordinator", "R1", {})
rec = core.recovered_this_week()
ok(rec["estimates_won"] == base["estimates_won"] + 1 and rec["won_value"] >= 3900,
   "a won estimate is counted with its value")
ok(rec["phc_renewed"] == base["phc_renewed"] + 1, "PHC renewals counted")
ok(rec["emergency_callbacks"] == 1, "human callbacks counted")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a),
   "automation counted or refused with a reason")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
