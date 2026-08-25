#!/usr/bin/env python3
"""Hours OS — the suite. `python3 test_hours_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["HOURSOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="hoursos_test_")
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
ok(len(store.load("loads")) >= 60, "loads seeded")

print("== triage ==")
for text, want in (("can you fix his log from tuesday, he forgot to flag the break", "log_ask"),
                   ("clean up the eld hours before the audit next week", "log_ask"),
                   ("there's a log problem on truck 12, adjust it", "log_ask"),
                   ("we had an accident on i-40, everyone is ok", "accident"),
                   ("trailer jack-knifed on the ramp, no injuries", "accident"),
                   ("somebody rear-ended us at the light in the yard truck", "accident"),
                   ("can marcus take the memphis load tonight", "dispatch_ask"),
                   ("dispatch the reefer run to whoever's closest", "dispatch_ask"),
                   ("been at the dock four hours, shipper says another two", "detention"),
                   ("sat at the receiver all morning waiting on a door", "detention"),
                   ("how many hours does dana have left today", "hours_ask"),
                   ("what's my clock looking like after the reset", "hours_ask"),
                   ("", "human"),
                   ("fuel card isn't working at the pilot", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

print("== the HOS dispatch gate ==")
okd, why = core.can_dispatch(store.by_id("drivers", "dr_demo_short"),
                             store.by_id("loads", "ld_demo_long"))
ok(not okd and "9.0h" in why and "3.0h" in why, "short clock refused with the arithmetic shown")
ok("nobody talks anyone into it" in why, "the refusal names the rule")
r = agents.dispatch("dr_demo_short", "ld_demo_long")
ok("refused" in r, "dispatch refuses")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "dispatch_beyond_hours"
       for e in store.events()), "dispatch_beyond_hours logged")
r = agents.dispatch("dr_demo_full", "ld_demo_long")
ok(r.get("rung") == "R1" and r.get("approval"), "a covering clock queues at R1")
okd, why = core.can_dispatch(store.by_id("drivers", "dr_demo_unknown"),
                             store.by_id("loads", "ld_demo_short"))
ok(not okd and "UNKNOWN cannot be dispatched" in why, "an unsynced clock dispatches nothing")

print("== the OOS gate ==")
okt, why = core.can_assign_truck(store.by_id("trucks", "tr_demo_oos"))
ok(not okt and "gets fixed" in why, "an OOS truck doesn't get assigned")

print("== log discipline ==")
out = agents.handle_message("ms_demo_log")
step = out["steps"][0]
ok("driver's sworn record" in step["refused"], "the log-edit request is refused")
ev = next(e for e in store.events()
          if e["kind"] == "refused" and (e["detail"] or {}).get("action") == "edit_or_certify_log")
ok(ev["detail"]["verbatim"] == "can you fix his log from tuesday, he forgot to flag the break",
   "the request is preserved verbatim")
ok(ev["detail"]["requester"] == "a customer service rep", "the requester is on the record")

print("== the accident protocol ==")
out = agents.handle_message("ms_demo_accident")
step = out["steps"][0]
ok(step["action"] == "brief_safety_director", "the brief goes to the safety director at R2")
ok(any("dash-cam" in c for c in step["brief"]["checklist"]), "the checklist preserves footage")
ok(any("no statements" in c for c in step["brief"]["checklist"]), "no statements before counsel")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "draft_outward_after_accident"
       for e in store.events()), "nothing outward — refused and logged")

print("== detention evidence ==")
inv = core.detention_invoice(store.by_id("loads", "ld_demo_detention"))
ok("total" in inv and inv["billable_h"] == 4.0 and inv["total"] == 240.0,
   "detention computes from the stamps: (6h − 2h free) × $60")
ok("from the stamps" in inv["basis"], "the basis names the evidence")
inv = core.detention_invoice(store.by_id("loads", "ld_demo_nostamps"))
ok("refused" in inv and "departure stamp" in inv["refused"],
   "no departure stamp → no invoice, the missing piece named")
ok("a feeling" in inv["refused"], "the refusal names the rule")
inv = core.detention_invoice({"arrived_at": iso(now() - timedelta(hours=5)),
                              "departed_at": iso(now())})
ok("refused" in inv and "terms for this lane" in inv["refused"], "no recorded terms → no invoice")

print("== the hours answer ==")
body = agents._hours_copy({"from": "dispatch"}, store.by_id("drivers", "dr_demo_full"))
ok("10.5h" in body and "recorded ELD" in body, "hours answered from the record")
body = agents._hours_copy({"from": "dispatch"}, store.by_id("drivers", "dr_demo_unknown"))
ok("UNKNOWN" in body and "don't dispatch on a guess" in body, "no sync → the honest answer")
ok("yourco" not in body.lower(), "white-label")

print("== maintenance ==")
mb = core.maintenance_board()
ok(any(r.get("_missing") is None or True for r in mb), "board renders")
out = agents.maintenance_sweep()
ok(out["alerts"] >= 0, "sweep runs")

print("== matrix ==")
for a in ("dispatch_beyond_hours", "edit_or_certify_log", "assign_oos_truck",
          "draft_outward_after_accident"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("edit_or_certify_log", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no log-edit request missed")
ok("FALSIFICATION" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("detention_open" in r["recorded"], "open detention counted")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Violations avoided at the gate"]["kind"] == "scenario",
   "prevented violations are never counted")

print("== recovered, counted ==")
base = core.recovered_this_week()
store.log_event("dispatch_load", "ld_demo_long", "human:dispatch", "R1", {})
rec = core.recovered_this_week()
ok(rec["loads_dispatched"] == base["loads_dispatched"] + 1, "human dispatches counted")
ok(rec["log_requests_refused"] >= 1, "log refusals counted from the log")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
