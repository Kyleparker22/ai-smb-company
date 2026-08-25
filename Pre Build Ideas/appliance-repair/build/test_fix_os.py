#!/usr/bin/env python3
"""Fix OS — the suite. `python3 test_fix_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["FIXOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="fixos_test_")
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
ok(len(store.load("units")) >= 400, "units seeded")
ok(len(store.load("jobs")) >= 250, "jobs seeded")
ok(len(store.load("claims")) >= 25, "claims seeded")
ok(len(core.recall_flagged()["rows"]) >= 2, "two units match the recorded recall list")
first_event = dict(store.events()[0])

print("== triage: the safety symptom reads first ==")
for text, want in (("I smell gas when the oven is on", "safety_symptom"),
                   ("the dryer sparked and there's a burning smell", "safety_symptom"),
                   ("dishwasher leaked all over the kitchen floor", "safety_symptom"),
                   ("there's smoke coming from the back of the fridge", "safety_symptom"),
                   ("my fridge is not cooling and it's still under warranty", "warranty_repair"),
                   ("the Kelmore range we bought in march just quit, warranty repair?", "warranty_repair"),
                   ("my dryer won't heat, what would a repair cost", "cod_repair"),
                   ("the washer stopped spinning mid cycle", "cod_repair"),
                   ("our dishwasher won't drain", "cod_repair"),
                   ("the ice maker quit working yesterday", "cod_repair"),
                   ("any update on my refrigerator repair", "status"),
                   ("when will the tech be out for my range", "status"),
                   ("is the compressor part in yet", "parts_ask"),
                   ("do you have the door gasket in stock for my washer", "parts_ask"),
                   ("", "human"),
                   ("what are your weekend hours", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]!r} → {want}")
ok(core.read_message("the dryer sparked and it's still under warranty")["label"]
   == "safety_symptom", "safety outranks the warranty word in the same breath")

print("== the safety script ==")
out = agents.handle_message("ms_demo_gas")
step = out["steps"][0]
ok(step["action"] == "draft_safety_reply", "the gas message drafts the safety reply")
ok(core.SAFETY_SCRIPT_GAS in step["draft"], "the gas script rides verbatim — leave + call the utility")
ok("I smell gas when the oven is on" in step["draft"],
   "the customer's own words survive verbatim, never softened")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "dismiss_safety_symptom"
       for e in store.events()), "dismiss_safety_symptom refused + logged")
ok(any(a["action"] == "draft_safety_reply" and a["state"] == "pending"
       for a in store.load("approvals")), "the safety draft queues at R1 — a human sends")
ok("yourco" not in step["draft"].lower(), "white-label")
store.upsert("messages", {"id": "ms_t_spark", "from": "Curt Bostic",
                          "text": "the dryer sparked and there's a burning smell",
                          "at": iso()})
out = agents.handle_message("ms_t_spark")
ok(core.SAFETY_SCRIPT_GENERAL in out["steps"][0]["draft"],
   "spark/burn gets the stop-using script verbatim")
ok("the dryer sparked and there's a burning smell" in out["steps"][0]["draft"],
   "spark language survives verbatim in the draft")

print("== the claim gate ==")
r = agents.submit_claim("cl_demo_incomplete")
ok("refused" in r, "incomplete claim refused")
ok("serial" in r["missing"], "missing serial named")
ok("purchase_proof_ref" in r["missing"], "missing proof-of-purchase ref named")
ok("free work" in r["refused"], "the refusal names the stake — a denied claim is free work")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "submit_incomplete_claim"
       for e in store.events()), "submit_incomplete_claim refused + logged")
ok(not any(a["action"] == "submit_incomplete_claim" for a in store.load("approvals")),
   "an incomplete submission never becomes an approvable row")
for name in ("force_submit", "force_submit_claim", "submit_anyway", "override_gate"):
    ok(not hasattr(core, name) and not hasattr(agents, name),
       f"no force-submit path: {name} does not exist")
r = agents.submit_claim("cl_demo_complete")
ok(r.get("ok") and r["gate"]["rung"] == "R1", "complete claim drafts at R1 — never auto-sends")
ok(not r["gate"].get("executed"), "the draft waits for a human release")
ap = next(a for a in store.load("approvals")
          if a["action"] == "submit_claim" and a["subject"] == "cl_demo_complete")
ok(core.gate.decide(ap["id"], "owner")["ok"], "a human releases the complete claim")

print("== narrative-matches-parts ==")
bad = {"serial": "X-1", "purchase_proof_ref": "POP-1", "failure_code": "F-44",
       "parts": ["drain pump", "check valve"],
       "narrative": "Unit presented with not draining. Corrected by replacing: drain pump."}
okc, why = core.can_submit(bad)
ok(not okc and "narrative-matches-parts" in why, "a narrative that skips a part fails the gate")
ok("check valve" in why, "the unmentioned part is named")

print("== the narrative assembles from the record ==")
n = agents.draft_narrative("cl_demo_complete")
ok("start relay" in n["narrative"] and "F-12" in n["narrative"],
   "the narrative carries the recorded parts and failure code")
ok("recorded diagnosis fields only" in n["basis"], "the basis names its discipline")
r = agents.draft_narrative("cl_demo_complete",
                           fields=list(core.NARRATIVE_FIELDS) + ["customer_fault_story"])
ok("refused" in r and "customer_fault_story" in r["refused"],
   "an uninvented field cannot be written into a narrative")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "invent_failure_narrative"
       for e in store.events()), "invent_failure_narrative refused + logged")

print("== parts-to-bring from unit memory ==")
out = agents.handle_message("ms_demo_fridge")
step = out["steps"][0]
ok(step["action"] == "log_ticket", "the fridge message opens a ticket")
ok(step["route"] == "warranty" and "in warranty" in out["steps"][0]["why"],
   "routed warranty from the RECORDED coverage, not the customer's word")
ok(step["parts_to_bring"] and step["parts_to_bring"][0] == "start relay",
   "the unit's own history leads the parts list")
ok("evaporator fan motor" in step["parts_to_bring"], "the recorded map fills the rest")
ok("own repair history" in step["parts_basis"], "the basis names the unit's memory")
job = store.by_id("jobs", step["job"])
ok(job and job.get("parts_to_bring") == step["parts_to_bring"],
   "the recorded parts list rides the persisted ticket")

print("== the recall flag, verbatim ==")
store.upsert("messages", {"id": "ms_t_recall", "from": "Dee Thorne",
                          "unit_id": "un_recall_1",
                          "text": "my Kelmore dishwasher won't start", "at": iso()})
out = agents.handle_message("ms_t_recall")
step = out["steps"][0]
notice = core.DEFAULT_RECALL_LIST["entries"][0]["notice"]
ok(step.get("recall_notice") == notice, "the recall notice rides the ticket VERBATIM")
ok(store.by_id("jobs", step["job"]).get("recall_notice") == notice,
   "the verbatim notice persists on the job record")
ok(any(e["kind"] == "flag_recall" for e in store.events()), "flag_recall logged")

print("== the COD clamp ==")
j0 = store.by_id("jobs", "jb_demo_cod")
ok(core.job_total(j0) == 280.0 and j0["authorized_amount"] == 280.0,
   "the demo job sits exactly at its recorded authorization")
r = agents.add_work("jb_demo_cod", "door seal", 60)
ok("refused" in r and "has no path" in r["refused"], "work past the authorization has no path")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "exceed_authorized_amount"
       for e in store.events()), "exceed_authorized_amount refused + logged")
ok(r.get("overage", {}).get("rung") == "R1", "the overage drafts at R1 for the customer")
ok(any(a["action"] == "draft_overage_request" and a["amount"] == 60
       and a["state"] == "pending" for a in store.load("approvals")),
   "the overage waits as an approval row")
ok(core.job_total(store.by_id("jobs", "jb_demo_cod")) == 280.0,
   "the job's work is untouched — the clamp is structural")
for name in ("force_add_work", "override_authorization", "exceed_authorization"):
    ok(not hasattr(core, name) and not hasattr(agents, name),
       f"no clamp bypass: {name} does not exist")
r = agents.add_work("jb_demo_cod_room", "vent brush", 40)
ok(r.get("ok") and r["total"] == 250.0, "work inside the authorization executes")
ok(any(e["kind"] == "add_work" and e.get("rung") == "R2" for e in store.events()),
   "in-authorization work logs at R2")
store.upsert("jobs", {"id": "jb_t_noauth", "customer": "Bea Pruitt", "kind": "cod",
                      "work": [], "opened_at": iso()})
r = agents.add_work("jb_t_noauth", "diagnostic", 90)
ok("refused" in r and "no recorded authorization" in r["refused"],
   "no recorded authorization → no work, and no overage draft either")
ok("overage" not in r, "an unrecorded authorization cannot be 'exceeded' into existence")

print("== matrix ==")
for a in ("submit_incomplete_claim", "exceed_authorized_amount", "dismiss_safety_symptom",
          "invent_failure_narrative"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
    ok(not core.matrix.promotable(a, 999)["promote"], f"{a} unpromotable even on a streak")
r = core.gate.act("submit_incomplete_claim", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
r = core.gate.act("exceed_authorized_amount", "probe", "x", {})
ok(r.get("refused"), "R0 clamp probe refused")
ok(not any(a["action"] in ("submit_incomplete_claim", "exceed_authorized_amount")
           and a["state"] == "pending" for a in store.load("approvals")),
   "an R0 action never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no safety symptom missed")
ok("GAS" in ev["costly_note"] and "FIRE" in ev["costly_note"],
   "the costly note names the fire/gas stake in caps")

print("== roi ==")
r = core.roi({})
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(r["recorded"]["blocked_claim_value"] > 0, "blocked claim value is counted, not asserted")
ok("re_rolled_visits" in r["recorded"], "re-rolled visits counted from the jobs")
labels = {l["label"]: l for l in r["lines"]}
ok(labels["COD disputes that never start"]["kind"] == "scenario",
   "COD disputes are a scenario, never a saving")
ok(labels["COD disputes that never start"]["value"] is None
   and "_missing" in labels["COD disputes that never start"],
   "the scenario line renders blank until the operator supplies it")
ok(labels["Office / paperwork hours"]["kind"] == "time_saved",
   "hours are time_saved — never summed into revenue")

print("== recovered, counted ==")
base = core.recovered_this_week()
c9 = next(c for c in store.load("claims") if not c.get("demo_tag") and not c.get("paid_at"))
c9["paid_at"] = iso(now() - timedelta(days=1))
store.upsert("claims", c9)
store.log_event("submit_claim", c9["id"], "human:owner", "R1", {})
rec = core.recovered_this_week()
ok(rec["claims_paid"] == base["claims_paid"] + 1, "a paid claim is counted")
ok(rec["paid_value"] >= base["paid_value"] + (c9.get("amount") or 0),
   "paid value counts the claim's own amount")
ok(rec["claims_submitted"] == base["claims_submitted"] + 1,
   "human releases counted; agent drafts are not")
ok("counted" in rec["note"], "recovered names its basis")

print("== sweeps skip demo rows ==")
store.upsert("messages", {"id": "ms_t_demo", "from": "Sal Renner",
                          "text": "our dishwasher won't drain", "at": iso(),
                          "demo_tag": "demo"})
agents.run_all()
ok(not store.by_id("messages", "ms_t_demo").get("handled_at"),
   "the message sweep leaves demo rows for the demo buttons")
ok(not store.by_id("claims", "cl_demo_incomplete").get("submitted_at"),
   "the claims sweep never touches demo rows")

print("== white-label ==")
drafts = [m.get("draft_reply", "") for m in store.load("messages") if m.get("draft_reply")]
ok(drafts and all("yourco" not in d.lower() for d in drafts),
   "no draft anywhere carries the yourco name")

print("== append-only ==")
n = len(store.events())
store.log_event("corrected", "cl_demo_complete", "human:owner", "R1",
                {"action": "submit_claim", "note": "a correction is a NEW event"})
ok(len(store.events()) == n + 1, "a correction appends; nothing is rewritten")
ok(store.events()[0]["id"] == first_event["id"]
   and store.events()[0]["kind"] == first_event["kind"],
   "the first event is untouched after everything above")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a),
   "automation counted or refused — never asserted")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
