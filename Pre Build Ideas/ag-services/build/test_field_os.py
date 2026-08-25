#!/usr/bin/env python3
"""Field OS — the suite. `python3 test_field_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["FIELDOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="fieldos_test_")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import agents, core, seed
from core import store

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
ok(len(store.load("jobs")) >= 600, "jobs seeded")
ok(len(store.load("growers")) == 180, "growers seeded")

print("== triage: drift reads first ==")
r = core.read_message("your rig sprayed right up to my fence and now my tomatoes are curling")
ok(r["label"] == "drift_exposure", "fence-line drift")
ok("regulator-grade" in r["why"], "drift why names the file")
ok(core.read_message("bees are dying all over my hives since tuesday")["label"] == "drift_exposure", "bee kill")
ok(core.read_message("the kids were outside when your plane went over our place")["label"] == "drift_exposure", "human exposure")
ok(core.read_message("my cattle have been acting sick since you sprayed the neighbor's quarter")["label"] == "drift_exposure", "livestock")
ok(core.read_message("we could smell the spray inside the house with the windows open")["label"] == "drift_exposure", "odor in house")
ok(core.read_message("what rate of atrazine should I run on my corn")["label"] == "chemical_question", "rate question")
ok(core.read_message("can you mix the fungicide with the foliar feed in one pass")["label"] == "chemical_question", "tank mix")
ok(core.read_message("can you get my beans sprayed this week before the rain")["label"] == "work_request", "work request")
ok(core.read_message("book me in for fall spreading on the north quarter")["label"] == "work_request", "book in")
ok(core.read_message("")["label"] == "human", "empty → human")
ok(core.read_message("invoice looks good, check is in the mail")["label"] == "human", "benign → human")

print("== the complaint protocol asserts nothing ==")
out = agents.handle_message("ms_demo_drift")
step = out["steps"][0]
ok(step["action"] == "log_complaint", "complaint logged")
ok("asserts nothing about cause" in step["said"], "protocol: no causation")
ok(any(e["kind"] == "refused" and e["detail"].get("action") == "assert_drift_cause"
       for e in store.events()), "assert_drift_cause refused + logged")
ok(any(a["action"] == "log_complaint" for a in store.load("approvals")) is False,
   "log_complaint is R2 — executes, no approval row")

print("== the chemical question goes unanswered ==")
out = agents.handle_message("ms_demo_rate")
ok(out["steps"][0].get("refused") == "routed unanswered", "chemical question refused")
ok(any(e["kind"] == "refused" and e["detail"].get("action") == "recommend_chemical_or_rate"
       for e in store.events()), "recommend_chemical_or_rate refused + logged")

print("== the as-applied billing gate ==")
okb, why = core.can_bill(store.by_id("jobs", "jb_demo_complete"))
ok(okb, "complete record bills")
ok("240 acres" in why, "bill reason cites the record")
okb, why = core.can_bill(store.by_id("jobs", "jb_demo_norec"))
ok(not okb, "incomplete record refused")
ok("applied_at" in why and "applicator_license" in why, "refusal names the missing fields")
ok("unprovable work" in why, "refusal names the stake")
r = agents.bill_job("jb_demo_norec")
ok("refused" in r, "bill_job refuses")
ok(any(e["kind"] == "refused" and e["detail"].get("action") == "bill_without_as_applied"
       for e in store.events()), "bill_without_as_applied logged")
r = agents.bill_job("jb_demo_complete")
ok(r.get("rung") == "R1" and r.get("approval"), "clean bill queues at R1")

print("== the RUP dispatch gate ==")
okd, why = core.can_dispatch(store.by_id("jobs", "jb_demo_rup"))
ok(not okd, "RUP without license refused")
ok("before the rig leaves the yard" in why, "refusal names the timing")
r = agents.dispatch_job("jb_demo_rup")
ok("refused" in r, "dispatch_job refuses")
ok(any(e["kind"] == "refused" and e["detail"].get("action") == "dispatch_rup_unlicensed"
       for e in store.events()), "dispatch_rup_unlicensed logged")
okd, why = core.can_dispatch(store.by_id("jobs", "jb_demo_norec"))
ok(okd and "APL-48211" in why, "RUP with license dispatches")
ok(core.can_dispatch({"rup": False})[0], "general-use dispatches")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no drift complaint missed")
ok("STATE-INVESTIGATION" in ev["costly_note"], "costly note names the stake")

print("== matrix ==")
for a in ("recommend_chemical_or_rate", "assert_drift_cause",
          "bill_without_as_applied", "dispatch_rup_unlicensed"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("recommend_chemical_or_rate", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a["action"] == "recommend_chemical_or_rate" and a["status"] == "pending"
           for a in store.load("approvals")), "R0 never becomes an approvable row")

print("== roi ==")
r = core.roi({})
ok("billable_unbilled" in r["recorded"], "billable count recorded")
line = next(l for l in r["lines"] if "complaint" in l["label"].lower())
ok(line["value"] is None and "not our number to model" in line["assumption"],
   "complaint line blank with the honest reason")
ok("MODEL" in r["label"].upper(), "ROI labelled a model")

print("== automation is counted ==")
a = core.automation()
ok("rate" in a, "automation rate field present")
ok(a.get("rate") is not None or "_missing" in a,
   "below-floor volume refuses a rate with a reason, never fakes one")

print("== new eval phrasings hold ==")
for text, want in (("the mist off your rig settled over our pond yesterday", "drift_exposure"),
                   ("our chickens have been acting sick since the spray plane came over", "drift_exposure"),
                   ("top-dress the wheat on the home quarter when you can", "work_request")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

print("== drafted copy ==")
body = agents._job_ack_copy({"from": "Renner"})
ok("Renner" in body and "weather" in body, "the job ack is honest about the weather's veto")
ok("not from silence" in body, "silence is named as the failure it is")
ok("yourco" not in body.lower(), "white-label: no yourco name in outward copy")
r = agents.bill_job("jb_demo_complete")
ok(r.get("draft") and "as-applied\nrecord" in r["draft"] or "as-applied" in r.get("draft", ""),
   "the invoice cover cites the as-applied record")
ok("applicator's license" in r["draft"], "the cover names the license on the record")

print("== recovered, counted ==")
base = core.recovered_this_week()
store.log_event("draft_invoice", "jb_demo_complete", "human:office", "R1", {})
store.log_event("dispatch_job", "jb_0001", "human:dispatch", "R1", {})
rec = core.recovered_this_week()
ok(rec["invoices_sent"] == base["invoices_sent"] + 1
   and rec["jobs_dispatched"] == base["jobs_dispatched"] + 1,
   "human sends are counted; agent drafts are not")
ok(rec["complaints_logged"] >= 1, "regulator-grade complaint logs are counted")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
