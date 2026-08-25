#!/usr/bin/env python3
"""Pump OS — the suite. `python3 test_pump_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["PUMPOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="pumpos_test_")
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
ok(len(store.load("systems")) == 400, "systems seeded")
ok(len(store.load("jobs")) >= 300, "jobs seeded")

print("== triage ==")
for text, want in (("sewage is backing up into the downstairs shower", "emergency"),
                   ("toilets are gurgling and black water is coming up the tub drain", "emergency"),
                   ("the septic alarm has been going off since midnight", "emergency"),
                   ("the pump alarm light is on in the yard", "emergency"),
                   ("is it the baffle or the leach field, what do you think", "diagnosis_ask"),
                   ("why does the drain field smell after heavy rain", "diagnosis_ask"),
                   ("it's been about three years, probably time to pump again", "due_service"),
                   ("can you pump the tank thursday when you're out this way", "due_service"),
                   ("need four porta johns for a wedding in june", "portable"),
                   ("job site needs two units and weekly service", "portable"),
                   ("", "human"),
                   ("invoice looks right, check is out today", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:42]} → {want}")

print("== the emergency ack ==")
out = agents.handle_message("ms_demo_backup")
step = out["steps"][0]
ok(step["action"] == "route_emergency", "backup routed as emergency")
ok("stop running water" in step["said"], "the ack gives the one safe instruction")
ok("diagnose on site, not on the phone" in step["said"].lower()
   or "not on the phone" in step["said"], "the ack restates the diagnosis rule")

print("== the phone-diagnosis refusal ==")
out = agents.handle_message("ms_demo_diag")
step = out["steps"][0]
ok(step["refused"] == "no phone diagnosis — the visit is the answer", "diagnosis refused")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "diagnose_by_phone"
       for e in store.events()), "diagnose_by_phone logged")
body = step["draft"]
ok("baffle" in body and "photos" in body, "the visit copy names what the tech actually checks")
ok(not any(w in body.lower() for w in ("probably", "sounds like", "most likely")),
   "no guess language in the reply")
ok("yourco" not in body.lower(), "white-label")

print("== the manifest billing gate ==")
okb, why = core.can_bill(store.by_id("jobs", "jb_demo_manifest"))
ok(okb and "MF-55120" in why, "complete record bills, citing the manifest")
okb, why = core.can_bill(store.by_id("jobs", "jb_demo_nomanifest"))
ok(not okb and "manifest_ref" in why, "missing manifest refused, field named")
ok("DEQ exhibit" in why, "the refusal names the regulatory stake")
r = agents.bill_job("jb_demo_nomanifest")
ok("refused" in r, "bill_job refuses")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "bill_without_manifest"
       for e in store.events()), "bill_without_manifest logged")
r = agents.bill_job("jb_demo_landapp")
ok("refused" in r and "permit" in r["refused"], "unpermitted land application refused")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "schedule_land_application_unpermitted"
       for e in store.events()), "land-application refusal logged")
r = agents.bill_job("jb_demo_manifest")
ok(r.get("rung") == "R1" and r.get("approval"), "clean job queues at R1")

print("== interval recall ==")
due = core.due_systems()
ok(any(r.get("overdue_days") is not None for r in due), "overdue systems counted")
ok(any(r.get("_missing") for r in due), "record-less systems read unknowable, never assumed")
s9 = {"id": "sy_x", "customer_name": "Dana Mercer", "interval_years": 3,
      "last_pumped": iso(now() - timedelta(days=4 * 365))}
store.upsert("systems", s9)
ok(core.recall_plan(s9)["action"] == "draft_recall", "an overdue system is due a recall")
s9["recalls"] = [{"at": iso(now() - timedelta(days=5))}]
ok(core.recall_plan(s9)["action"] == "none", "30-day cooldown holds")
s9["recalls"] = [{"at": iso(now() - timedelta(days=100 - i))} for i in range(3)]
ok("silence is an answer" in core.recall_plan(s9)["why"], "ladder exhausts at 3")
b1 = agents._recall_copy(s9, {}, 1)
ok("Dana" in b1 and "3 years" in b1, "recall copy names the interval fact")
b2 = agents._recall_copy(s9, {}, 2)
ok("fix our records" in b2, "touch 2 offers the honest exit")
b3 = agents._recall_copy(s9, {}, 3)
ok("leave it here" in b3, "touch 3 closes gently")

print("== matrix ==")
for a in ("diagnose_by_phone", "bill_without_manifest",
          "schedule_land_application_unpermitted"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("diagnose_by_phone", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a_["action"] == "diagnose_by_phone" and a_["state"] == "pending"
           for a_ in store.load("approvals")), "R0 never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no emergency missed")
ok("BIOHAZARD" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("overdue_systems" in r["recorded"], "overdue count recorded")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Recalled pump-outs"]["value"] is None,
   "revenue line blank without the operator's avg ticket")
ok(labels["The manifest file"]["kind"] == "scenario", "the audit is a scenario, never a saving")

print("== recovered, counted ==")
base = core.recovered_this_week()
j9 = store.by_id("jobs", "jb_demo_manifest")
j9["billed_at"] = iso(now() - timedelta(days=1))
store.upsert("jobs", j9)
store.log_event("draft_recall", "sy_x", "human:recall", "R1", {})
store.log_event("draft_portable_order", "ms_1", "human:frontdesk", "R1", {})
rec = core.recovered_this_week()
ok(rec["jobs_billed"] == base["jobs_billed"] + 1, "a billed job is counted")
ok(rec["recalls_sent"] == 1 and rec["portable_orders"] == 1,
   "human sends are counted; agent drafts are not")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
