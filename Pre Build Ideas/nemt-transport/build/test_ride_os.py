#!/usr/bin/env python3
"""Ride OS — the suite. `python3 test_ride_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["RIDEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="rideos_test_")
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
ok(len(store.load("trips")) >= 200, "trips seeded")

print("== triage: the condition read comes first ==")
for text, want in (("grandma seems confused today, more than usual", "condition_change"),
                   ("mr osei couldn't stand up from the chair this morning", "condition_change"),
                   ("she's slurring her words a little on the ride", "condition_change"),
                   ("driver says she fell getting into the van", "condition_change"),
                   ("need to reschedule tuesday's pickup to the afternoon", "schedule"),
                   ("can the ride come earlier on thursday", "schedule"),
                   ("the claim for last week's trips was denied", "billing"),
                   ("the van was 40 minutes late and she missed the appointment", "complaint"),
                   ("driver didn't show for the 8am pickup", "complaint"),
                   ("", "human"),
                   ("what's the office number for the billing department", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

print("== the condition protocol ==")
out = agents.handle_message("ms_demo_cond")
step = out["steps"][0]
ok(step["action"] == "escalate_condition", "condition escalates at R2")
ok("we're drivers, not clinicians" in step["draft"].lower(), "the ack says who we are and aren't")
ok("probably" not in step["draft"].lower() and "fine" not in step["draft"].lower(),
   "no reassurance anywhere in the ack")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "assess_patient_condition"
       for e in store.events()), "assess_patient_condition refused + logged")
ev = next(e for e in store.events() if e["kind"] == "escalate_condition")
ok(ev["detail"]["verbatim"] == "grandma seems confused today, more than usual",
   "the words travel verbatim")
ok("yourco" not in step["draft"].lower(), "white-label")

print("== the trip-log gate ==")
okb, why = core.can_bill(store.by_id("trips", "tp_demo_nolog"))
ok(not okb and "dropoff_odo" in why and "signature_ref" in why, "missing fields named")
ok("Medicaid audit" in why, "the stake named")
r = agents.bill_trip("tp_demo_nolog")
ok("refused" in r, "the bill path refuses")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "bill_without_trip_log"
       for e in store.events()), "bill_without_trip_log logged")
r = agents.bill_trip("tp_demo_logged")
ok(r.get("rung") == "R1" and r.get("approval"), "a complete log bills at R1")

print("== the never-bump rule ==")
r = agents.bump_trip("tp_demo_dialysis")
ok("refused" in r and "medical harm, not a late ride" in r["refused"], "dialysis never bumps")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "bump_protected_trip"
       for e in store.events()), "bump_protected_trip logged")
out = agents.handle_message("ms_demo_bump")
ok(out["steps"][0]["action"] == "escalate_conflict",
   "a schedule ask against a protected trip escalates to a human")
r = agents.bump_trip(store.load("trips")[2] if store.load("trips")[2].get("purpose") not in
                     ("dialysis", "chemo", "radiation") else {"id": "x", "purpose": "dental"})
ok(True, "smoke: non-protected path runs")

print("== the credential gate ==")
oka, why = core.can_assign(store.by_id("drivers", "dr_demo_lapsed"))
ok(not oka and "expired: cpr" in why and "missing: securement" in why, "each lapse named")
ok("45mph" in why, "the stake named")
r = agents.assign_driver("tp_demo_dialysis", "dr_demo_lapsed")
ok("refused" in r, "the assignment refuses")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "assign_uncredentialed_driver"
       for e in store.events()), "assign_uncredentialed_driver logged")
r = agents.assign_driver("tp_demo_dialysis", "dr_demo_clean")
ok(r.get("rung") == "R1" and r.get("approval"), "current credentials assign at R1")

print("== boards ==")
store.upsert("trips", {"id": "tp_nolog_real", "patient_ref": "PT-9001", "purpose": "dental",
                       "amount": 38, "completed_at": iso(now() - timedelta(days=1)),
                       "trip_log": {"pickup_odo": 1, "dropoff_odo": None, "pickup_at": None,
                                    "dropoff_at": None, "signature_ref": None}})
ub = core.unbillable_board()
ok(ub["value"] >= 38 and any(r["trip"] == "tp_nolog_real" for r in ub["rows"]),
   "unbillable trips counted with dollars")
tb = core.tomorrow_board()
ok(any(r["never_bump"] for r in tb), "protected trips flagged on the board")

print("== copy ==")
sc = agents._schedule_copy({"from": "Elena"})
ok("hold their slots no matter what" in sc, "the schedule copy states the never-bump rule")
cc = agents._complaint_copy({"from": "Elena"})
ok("same facts" in cc and "plainly" in cc, "the complaint copy owns it with the log open")

print("== matrix ==")
for a in ("assess_patient_condition", "bill_without_trip_log", "bump_protected_trip",
          "assign_uncredentialed_driver"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("assess_patient_condition", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no condition change missed")
ok("GRANDMOTHER" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("unbillable_value" in r["recorded"], "unbillable counted")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["The never-bump record"]["kind"] == "scenario", "the rule is never a saving")

print("== recovered, counted ==")
base = core.recovered_this_week()
t9 = store.by_id("trips", "tp_demo_logged")
t9["billed_at"] = iso(now() - timedelta(hours=2))
store.upsert("trips", t9)
rec = core.recovered_this_week()
ok(rec["trips_billed"] == base["trips_billed"] + 1 and rec["billed_value"] >= 38,
   "billed trips counted with dollars")
ok(rec["condition_escalations"] >= 1, "escalations counted")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
