#!/usr/bin/env python3
"""Cab OS — the suite. `python3 test_cab_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["CABOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="cabos_test_")
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
ok(len(store.load("units")) >= 380, "units seeded")

print("== triage: entrapment first ==")
for text, want in (("we're stuck in the elevator at the medical building", "entrapment"),
                   ("there are people trapped between floors in the east car", "entrapment"),
                   ("someone's inside and the doors won't open", "entrapment"),
                   ("my kids are in there and it's stuck between 3 and 4", "entrapment"),
                   ("the service elevator is down again at the loading dock", "unit_down"),
                   ("escalator stopped this morning and won't restart", "unit_down"),
                   ("elevator won't open on 5, nobody inside", "unit_down"),
                   ("there's a grinding noise on the ride up", "noise"),
                   ("the escalator makes a squeal at the top landing", "noise"),
                   ("when is our cat 1 test due this year", "inspection"),
                   ("need to schedule the annual inspection with the state guy", "inspection"),
                   ("", "human"),
                   ("invoice received, processing this week", "human")):
    ok(core.read_call(text)["label"] == want, f"triage: {text[:42]} → {want}")

print("== the entrapment protocol ==")
out = agents.handle_call("cl_demo_entrap")
step = out["steps"][0]
ok(step["action"] == "dispatch_entrapment", "entrapment dispatches at R2")
ok("NEVER advise" in step["said"] and "self-evacuation" in step["said"],
   "the script forbids self-evacuation, verbatim")
ok("safest place" in step["said"], "the script tells passengers the car is safest")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "advise_self_evacuation"
       for e in store.events()), "advise_self_evacuation refused + logged")

print("== red-tag discipline ==")
r = agents.reactivate("un_demo_red")
ok("refused" in r and "fatality investigation" in r["refused"],
   "no sign-off → the unit stays down, stake named")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "reactivate_red_tagged"
       for e in store.events()), "reactivate_red_tagged logged")
ok(store.by_id("units", "un_demo_red")["red_tagged_at"], "the tag did not move")
r = agents.reactivate("un_demo_red", mechanic_signoff="MECH-armando-2214")
ok(r.get("reactivated"), "the mechanic's recorded sign-off clears it")
u = store.by_id("units", "un_demo_red")
ok(u["red_tagged_at"] is None and u["cleared_by"] == "MECH-armando-2214",
   "the clearance is recorded with who")

print("== the test calendar: UNKNOWN, never compliant ==")
st = core.unit_state(store.by_id("units", "un_demo_unknown"))
ok(st["tests"]["cat1"]["state"] == "unknown" and "never compliant" in st["tests"]["cat1"]["why"],
   "no record reads UNKNOWN")
st = core.unit_state({"id": "x", "tests": {"cat1": iso(now() - timedelta(days=400))}})
ok(st["tests"]["cat1"]["state"] == "overdue", "overdue computes from the record")

print("== the scope engine ==")
v = agents.scope_ticket("un_000", "kicked-in panel, vandalism at the lobby")
ok(v["verdict"] == "billable" and v["clause"] == "X-2", "vandalism billable, clause cited")
ok("X-2" in v["draft"] and "quote comes first" in v["draft"], "the draft quotes the clause")
v = agents.scope_ticket("un_000", "door operator sticking on 3")
ok(v["verdict"] == "in_contract" and v["clause"] == "M-1", "door operator covered, clause cited")
v = agents.scope_ticket("un_000", "water damage from the roof leak")
ok(v["verdict"] == "ambiguous", "contract silence is ambiguous, never billable")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "assert_billable_off_silence"
       for e in store.events()), "assert_billable_off_silence logged")

print("== drafted copy ==")
n = agents._noise_copy({"from": "Meridian Tower"})
ok("before it becomes a shutdown" in n, "the noise copy explains why it matters")
ok("yourco" not in n.lower(), "white-label")

print("== matrix ==")
for a in ("advise_self_evacuation", "reactivate_red_tagged",
          "mark_test_compliant_without_record", "assert_billable_off_silence"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("advise_self_evacuation", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a_["action"] == "advise_self_evacuation" and a_["state"] == "pending"
           for a_ in store.load("approvals")), "R0 never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no entrapment missed")
ok("HUMAN IN A BOX" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("tests_due" in r["recorded"], "tests due counted")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["The entrapment log"]["kind"] == "scenario", "the log is a scenario, never a saving")

print("== recovered, counted ==")
base = core.recovered_this_week()
store.log_event("draft_billable", "un_000", "human:office", "R1", {})
u9 = store.by_id("units", "un_000")
u9.setdefault("tests", {})["cat1"] = iso(now() - timedelta(days=1))
store.upsert("units", u9)
rec = core.recovered_this_week()
ok(rec["billables_sent"] == 1, "human-sent billables counted")
ok(rec["tests_recorded"] >= base["tests_recorded"] + 1, "recorded tests counted")
ok(rec["entrapments_dispatched"] >= 1, "entrapment dispatches counted")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
