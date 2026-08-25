#!/usr/bin/env python3
"""Move OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["MOVEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="moveos-test-")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import agents, core
from core import store
from _kit.store import iso, now

PASS = FAIL = 0


def ok(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL  {msg}")


# ---------------------------------------------------------------- binding needs a survey
okb, why = core.can_issue_binding({"survey_id": "s1", "inventory_items": 120})
ok(okb, "a surveyed, inventoried move can go binding")
okb, why = core.can_issue_binding({"survey_id": None, "inventory_items": None})
ok(not okb and "guess is not a binding number" in why, "no survey → no binding estimate")
okb, why = core.can_issue_binding({"survey_id": "s1", "inventory_items": None})
ok(not okb and "inventory" in why, "a survey without an inventory still refuses")

store.wipe()
store.save("config", {"company": "t", "claim_rules": core.DEFAULT_CLAIM_RULES})
store.save("moves", [{"id": "m_ns", "estimate_type": "binding", "survey_id": None},
                     {"id": "m_ok", "estimate_type": "binding", "survey_id": "s1",
                      "inventory_items": 100, "binding_amount": 4000}])
r = agents.issue_binding("m_ns")
ok("refused" in r, "the agent path refuses the unsurveyed binding estimate")
ok(not any(a for a in store.load("approvals")), "…and no draft row exists")
r = agents.issue_binding("m_ok")
ok(r.get("approval"), "the surveyed one drafts at R1")

# ---------------------------------------------------------------- the charge clamp
m = {"id": "m1", "estimate_type": "binding", "binding_amount": 4200,
     "change_orders": [{"desc": "packing", "amount": 400, "signed_at": iso(now())},
                       {"desc": "driver extra", "amount": 850, "signed_at": None}]}
c = core.final_charges(m)
ok(c["total"] == 4600, "final charges = estimate + SIGNED change orders only")
ok(len(c["excluded"]) == 1 and "conversation, not a charge" in c["excluded"][0]["why"],
   "the unsigned change order is excluded and named")
c = core.final_charges({"id": "m2", "estimate_type": "binding"})
ok(c.get("_missing"), "a binding move with no recorded amount cannot be charged")
c = core.final_charges({"id": "m3", "estimate_type": "non_binding",
                        "actual_hours": 6.5, "hourly_rate": 159})
ok(c["total"] == round(6.5 * 159, 2) and "non-binding" in c["basis"],
   "a non-binding move bills recorded hours and says so")
c = core.final_charges({"id": "m4", "estimate_type": "non_binding"})
ok(c.get("_missing"), "no recorded hours → nothing can be charged")

# ---------------------------------------------------------------- claims
store.save("conditions", [
    {"id": "l1", "move_id": "mv1", "item": "dresser", "kind": "load", "damage": []},
    {"id": "d1", "move_id": "mv1", "item": "dresser", "kind": "delivery", "damage": ["cracked leg"]},
    {"id": "l2", "move_id": "mv2", "item": "sofa", "kind": "load", "damage": ["torn upholstery"]},
    {"id": "d2", "move_id": "mv2", "item": "sofa", "kind": "delivery", "damage": ["torn upholstery"]},
])
v = core.claim_check({"move_id": "mv1", "item": "dresser"})
ok(v["assessable"] and v["new_damage"] == ["cracked leg"], "the evidence pair assesses new damage")
v = core.claim_check({"move_id": "mv2", "item": "sofa"})
ok(v["assessable"] and v["new_damage"] == [],
   "pre-existing damage produces an honest 'no new damage'")
v = core.claim_check({"move_id": "mv9", "item": "mirror"})
ok(not v["assessable"] and "asserts nothing either way" in v["refused"],
   "missing records → cannot assess, in either direction")

clock = core.claim_clock({"filed_at": iso(now() - timedelta(days=10))})
ok(clock["ack_days_left"] in (19, 20), "the acknowledgment clock computes from filing")
ok(clock["label"].startswith("DATE ALERT"), "the clock is a date alert, not legal advice")
ok("replace with counsel-reviewed" in clock["rules_source"], "the rule set names itself a default")

# claim settle path
store.save("claims", [{"id": "c_ok", "move_id": "mv1", "item": "dresser", "filed_at": iso()},
                      {"id": "c_no", "move_id": "mv9", "item": "mirror", "filed_at": iso()}])
store.save("approvals", [])
r = agents.settle_claim("c_no")
ok("refused" in r, "a claim without records cannot draft a settlement")
r = agents.settle_claim("c_ok")
ok(r.get("gate", {}).get("approval"), "the evidenced claim drafts at R1")

# ---------------------------------------------------------------- triage + eval
ok(core.read_message("the dresser arrived with a cracked leg")["label"] == "claim_report",
   "a damage report classifies")
ok(core.read_message("how much to move a 3 bedroom house")["label"] == "quote_request",
   "a quote ask classifies")
ok(core.read_message("")["label"] == "human", "empty routes to a person")
ev = core.run_eval()
ok(ev["costly_label"] == "claim_report" and ev["costly_missed"] == 0,
   f"zero missed claims in the shipped eval ({ev['costly_missed']})")
ok("REGULATORY EXPOSURE" in ev["costly_note"], "the eval names the stake")

# handle path starts the clock at the report
store.save("messages", [{"id": "msg1", "move_id": "mv1", "item": "dresser",
                         "text": "the dresser arrived with a cracked leg",
                         "at": iso(now() - timedelta(hours=2))}])
r = agents.handle_message("msg1")
ok(r["steps"][0]["action"] == "start_claim_clock", "the clock starts first")
claims = [c for c in store.load("claims") if c.get("move_id") == "mv1" and c["id"] not in ("c_ok",)]
ok(any(c["filed_at"] == store.by_id("messages", "msg1")["at"] for c in claims),
   "the claim carries the REPORT's timestamp")

# ---------------------------------------------------------------- R0 probes
for action in ("issue_binding_without_survey", "charge_above_estimate",
               "condition_delivery_on_extra_payment"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("issue_binding_without_survey", "charge_above_estimate",
                           "condition_delivery_on_extra_payment")
           for a in core.gate.pending()), "no R0 action reached the approval queue")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Survey-backed binding margin"]["value"] is None,
   "the margin line is blank without the operator's lift")
ok(labels["The clamp, as reputation"]["kind"] == "scenario",
   "the clamp is never monetized by us")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("two boxes never showed up at the new house", "claim_report"),
                   ("the washer got dented somewhere between the truck and the basement", "claim_report"),
                   ("price for moving a 2 bedroom apartment to austin", "quote_request")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

# ---------------------------------------------------------------- drafted copy
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

claim9 = {"id": "cm9", "move_id": "mv1", "item": "dresser",
          "filed_at": _iso(_now() - timedelta(days=1))}
clock9 = core.claim_clock(claim9)
ack = agents._ack_copy(claim9, clock9)
ok(str(clock9["ack_due"])[:10] in ack, "the ack states the clock date out loud")
ok("confirms receipt" in ack and "claims adjuster" in ack,
   "the ack is a receipt, not an assessment")
ok(not any(w in ack.lower() for w in ("our fault", "we're liable", "denied", "not covered")),
   "no fault taken, no claim denied")
ok("yourco" not in ack.lower(), "white-label: no yourco name in outward copy")

sv = agents._survey_copy()
ok("binding number needs" in sv and "survey" in sv, "the survey reply explains the rule")
ok("$" not in sv, "no number in the survey reply — a guess is not a binding number")

# handle_message drafts the ack alongside the clock
store.upsert("messages", {"id": "mg9", "move_id": "mv1", "at": _iso(_now()),
                          "text": "the dresser arrived with a cracked leg"})
out = agents.handle_message("mg9")
new_claim = next(c for c in store.load("claims") if c.get("text", "").startswith("the dresser"))
ok(new_claim.get("ack_draft"), "the ack draft is recorded on the claim")
ok(any(a_["action"] == "draft_claim_ack" and a_["subject"] == new_claim["id"]
       for a_ in store.load("approvals")), "the ack queues at R1")

# ---------------------------------------------------------------- the deadline alarm
store.upsert("claims", {"id": "cm10", "move_id": "mv1", "item": "sofa",
                        "filed_at": _iso(_now() - timedelta(days=27))})
out = agents.deadline_sweep()
ok(out["alerts"] >= 1, "a claim inside 5 days of its ack deadline raises the alarm")
ok(any(e["kind"] == "claim_deadline_alert" and e["subject"] == "cm10"
       for e in store.events()), "the alarm lands in the log at R2")
out = agents.deadline_sweep()
ok(out["alerts"] == 0, "the 3-day alarm cooldown holds")

# ---------------------------------------------------------------- recovered, counted
rec = core.recovered_this_week()
ok(rec["acks_sent"] == 0 and rec["bindings_issued"] == 0, "nothing sent → zeros, honestly")
store.log_event("draft_claim_ack", "cm9", "human:claimsdesk", "R1", {})
store.log_event("draft_binding_estimate", "mv1", "human:sales", "R1", {})
rec = core.recovered_this_week()
ok(rec["acks_sent"] == 1 and rec["bindings_issued"] == 1,
   "human sends are counted; agent drafts are not")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
