#!/usr/bin/env python3
"""Pane OS — the suite. `python3 test_pane_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["PANEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="paneos_test_")
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
ok(len(store.load("orders")) >= 200, "orders seeded across the pipeline")
ok(len(store.load("remakes")) >= 20, "remake ledger seeded")
ok(len(store.load("messages")) >= 12, "messages seeded")
ev_first = store.events()[0]

print("== triage: the board-up reads first ==")
for c in core.EVAL_CASES:
    ok(core.read_message(c["input"])["label"] == c["label"],
       f"triage: {c['input'][:46]} → {c['label']}")

print("== the board-up dispatch path ==")
out = agents.handle_message("ms_demo_breakin")
ok(out["steps"][0]["action"] == "dispatch_board_up", "the dispatch goes FIRST")
ok("security event" in out["steps"][0]["why"], "the dispatch names the stake")
ok(any(e["kind"] == "dispatch_board_up" and e["rung"] == "R2" for e in store.events()),
   "dispatch executed at R2 and logged")
ok(out["steps"][1]["action"] == "draft_boardup_reply", "the reply drafts second")
ok("board-up crew is dispatched" in out["steps"][1]["draft"], "the customer hears what moved")
ok("yourco" not in out["steps"][1]["draft"].lower(), "board-up copy is white-label")

print("== sweeps skip demo fixtures ==")
sw = agents.release_sweep()
ok(sw["queued"] >= 1, "the sweep queues real releasable orders")
ok(sw["held"] >= 1, "the sweep holds gate failures rather than releasing them")
ok(not any(str(a.get("subject", "")).startswith("or_demo_")
           for a in store.load("approvals")), "no demo order was swept")
ok(not any(str(e.get("subject", "")).startswith("or_demo_")
           and e["kind"] in ("release_to_fabricator", "queued_for_approval")
           for e in store.events()), "no demo order release event from the sweep")

print("== the measure-twice gate ==")
r = agents.release_order("or_demo_single")
ok("refused" in r, "one measurement → refused")
ok("the second is missing" in r["refused"], "the refusal names the gap")
ok("Reyes (crew A)" in r["refused"] and "36.0" in r["refused"],
   "the single reading is quoted back as a recorded act — who and values")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action")
       == "release_order_without_matching_measurements" for e in store.events()),
   "release_order_without_matching_measurements logged")
r = agents.release_order("or_demo_mismatch")
ok("refused" in r, "mismatched beyond tolerance → refused")
ok("0.125" in r["refused"], "the refusal cites the recorded tolerance")
ok("36.0" in r["refused"] and "36.5" in r["refused"], "the refusal cites both values")
ok("Δ0.5" in r["refused"], "the refusal shows the disagreement")
r = agents.release_order("or_demo_matched")
ok(r.get("rung") == "R1" and r.get("approval"), "matched pair → released to the R1 click")
ok(not hasattr(core, "force_release") and not hasattr(agents, "force_release"),
   "no force path exists")
ok(not hasattr(agents, "release_unchecked") and not hasattr(core, "override_tolerance"),
   "no unchecked or override path exists")

print("== the deposit wall (structural) ==")
r = agents.release_order("or_demo_nodeposit")
ok("refused" in r and "no recorded deposit" in r["refused"], "matched pair, no deposit → refused")
ok("no second buyer" in r["refused"], "the refusal names why the wall exists")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action")
       == "release_fabrication_without_deposit" for e in store.events()),
   "release_fabrication_without_deposit logged")

print("== the safety-location rule ==")
r = agents.check_quote("door", "annealed")
ok("refused" in r, "annealed in a door → refused")
ok("safety glazing" in r["refused"] and "code violations cheaper" in r["refused"],
   "the refusal cites the rule and the stance")
ok("rules_source" in r and "not legal advice" in r["rules_source"],
   "the rule table names its source honestly")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action")
       == "quote_annealed_in_safety_location" for e in store.events()),
   "quote_annealed_in_safety_location logged")
ok("ok" in core.safety_check("tub_shower", "tempered"), "tempered in a shower passes")
ok("ok" in core.safety_check("kitchen_backsplash", "annealed"),
   "annealed in an unflagged location passes")
out = agents.handle_message("ms_demo_annealed")
step = out["steps"][0]
ok(step.get("refused") and "glazing in a door" in step["refused"],
   "the quote flow runs the safety check and cites the rule")
ok("don't sell code violations" in step["draft"], "the draft says the stance to the customer")
ok("yourco" not in step["draft"].lower(), "quote copy is white-label")

print("== the lead-time promise rule ==")
r = agents.answer_lead_time("or_demo_undated")
ok("refused" in r and "from hope" in r["refused"], "no fabricator date → the promise refuses")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action")
       == "promise_undated_lead_time" for e in store.events()),
   "promise_undated_lead_time logged")
r = agents.answer_lead_time("or_demo_dated")
ok(r.get("date") and "recorded promised date" in r["basis"],
   "a recorded fabricator date is cited, not hoped")
out = agents.handle_message("ms_demo_leadtime")
ok("hasn't confirmed a date" in out["steps"][0]["draft"],
   "the undated status reply says so instead of inventing a date")
ok(out["steps"][0].get("refused"), "the undated reply carries the refusal")
out = agents.handle_message("ms_demo_status")
ok("recorded promised date" in out["steps"][0]["draft"], "the dated status reply cites the record")
ok("yourco" not in out["steps"][0]["draft"].lower(), "status copy is white-label")

print("== the remake ledger, counted ==")
rr = core.remake_rate()
ok(rr.get("rate") is not None, "the remake rate is counted (enough completed orders)")
ok("counted from the remake ledger" in rr["note"], "the rate names its basis")
ok(set(rr["by_cause"]) == {"measure", "fab", "install", "customer"},
   "cause codes: measure / fab / install / customer")
ok(rr["by_cause"]["measure"] >= 1, "measurement remakes are in the ledger")
rr2 = core.remake_rate(floor=10_000)
ok("_missing" in rr2 and "noise wearing a percent sign" in rr2["_missing"],
   "below the floor the rate refuses rather than estimates")

print("== matrix ==")
for a in ("release_order_without_matching_measurements", "quote_annealed_in_safety_location",
          "promise_undated_lead_time", "release_fabrication_without_deposit"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
for a in ("release_order_without_matching_measurements", "release_fabrication_without_deposit"):
    r = core.gate.act(a, "probe", "x", {})
    ok(r.get("refused"), f"R0 probe refused: {a}")
ok(not any(a_["action"] in core.matrix.never_promote() and a_["state"] == "pending"
           for a_ in store.load("approvals")), "no R0 action ever becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["n"] >= 15, "15+ labelled cases")
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no board-up emergency missed")
ok("AN OPEN STOREFRONT AT NIGHT IS A SECURITY EVENT" in ev["costly_note"],
   "the costly note names the stake in caps")

print("== roi ==")
r = core.roi({})
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
labels = {l["label"]: l for l in r["lines"]}
ok(labels["Deposit float, collected before fabrication"]["kind"] == "cash_timing",
   "deposit float is cash timing, not new revenue")
ok(labels["Deposit float, collected before fabrication"]["value"] is not None,
   "deposit float computes from the counted ledger")
rem = labels["Remakes avoided at the measure-twice gate"]
ok(rem["kind"] == "scenario", "remakes avoided is a scenario, never a counted saving")
ok(rem["value"] is None and "remake_lift" in (rem.get("_missing") or ""),
   "the scenario line renders blank until the operator supplies the lift")
ok("remakes_12mo" in r["recorded"] and "avg_remake_cost" in r["recorded"],
   "the ledger count and recorded cost ride in as recorded inputs")
r2 = core.roi({"remake_lift": 0.7})
ok(({l["label"]: l for l in r2["lines"]}
    ["Remakes avoided at the measure-twice gate"]["value"] or 0) > 0,
   "with the operator's lift the scenario computes and shows its arithmetic")

print("== recovered, counted (baseline delta) ==")
base = core.recovered_this_week()
o9 = store.by_id("orders", "or_demo_nodeposit")
o9["deposit_paid_at"] = iso(now() - timedelta(days=1))
o9["deposit_amount"] = 1700
store.upsert("orders", o9)
o8 = store.by_id("orders", "or_demo_dated")
o8["installed_at"] = iso(now())
store.upsert("orders", o8)
store.log_event("release_to_fabricator", "or_demo_matched", "human:owner", "R1", {})
rec = core.recovered_this_week()
ok(rec["deposit_count"] == base["deposit_count"] + 1
   and rec["deposits_collected"] >= base["deposits_collected"] + 1700,
   "collected deposits counted against the baseline")
ok(rec["installs_done"] == base["installs_done"] + 1, "installs counted against the baseline")
ok(rec["releases_approved"] == base["releases_approved"] + 1,
   "human-approved releases counted; agent queue events are not")
ok(rec["boardups_dispatched"] >= 1, "the board-up dispatch is counted")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a),
   "automation counted or refused — never asserted")

print("== the log is append-only ==")
n1 = len(store.events())
store.log_event("note", "x", "human:test", None, {})
evs = store.events()
ok(len(evs) == n1 + 1, "events only append")
ok(evs[0]["id"] == ev_first["id"] and evs[0]["kind"] == ev_first["kind"],
   "the first event is untouched — corrections are new events")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
