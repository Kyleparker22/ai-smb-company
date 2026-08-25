#!/usr/bin/env python3
"""Route OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["ROUTEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="routeos-test-")
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


# ---------------------------------------------------------------- triage + eval
c = core.read_message("my dog licked the baseboard where they sprayed")
ok(c["label"] == "exposure" and c["instruction"] == core.POISON_INSTRUCTION,
   "an exposure carries the Poison Control instruction")
ok(core.read_message("toddler got into the bait station")["label"] == "exposure",
   "a child near bait is an exposure")
ok(core.read_message("is it safe for the kids to go back inside now")["label"] == "safety_question",
   "a re-entry question is a safety question")
ok(core.read_message("still seeing ants in the kitchen")["label"] == "reservice",
   "a still-seeing message is a reservice")
ok(core.read_message("please cancel the service")["label"] == "cancellation", "a cancel routes")
ok(core.read_message("")["label"] == "human", "empty routes to a person")

ev = core.run_eval()
ok(ev["costly_label"] == "exposure" and ev["costly_missed"] == 0,
   f"zero missed exposures in the shipped eval ({ev['costly_missed']})")
ok("POISONING INCIDENT" in ev["costly_note"], "the eval names the stake")

# ---------------------------------------------------------------- handling
store.wipe()
store.save("config", {"company": "t"})
store.save("messages", [
    {"id": "m_e", "text": "my cat got into the granules by the fence"},
    {"id": "m_s", "text": "what's in the spray you used near the vegetable garden"},
    {"id": "m_r", "text": "the roaches came back, need a retreat", "account_id": "a1"},
])
store.save("accounts", [{"id": "a1", "name": "x", "status": "active"}])
r = agents.handle_message("m_e")
ok(r["steps"][0]["said"] == core.POISON_INSTRUCTION,
   "the exposure reply IS the Poison Control instruction, nothing else")
r = agents.handle_message("m_s")
ok(r["steps"][0].get("refused") == "routed unanswered", "a safety question goes unanswered")
ok(any(e["detail"].get("action") == "answer_chemical_safety"
       for e in store.events(kind="refused", subject="m_s")), "the refusal is logged")
r = agents.handle_message("m_r")
ok(any(e["kind"] == "churn_signal" and e["subject"] == "a1" for e in store.events()),
   "a reservice records the churn signal on the account")

# ---------------------------------------------------------------- billing integrity
store.save("services", [
    {"id": "s_skip", "account_id": "a1", "status": "skipped", "skip_reason": "locked gate",
     "scheduled_at": iso(now() - timedelta(days=2))},
    {"id": "s_done", "account_id": "a1", "status": "completed",
     "scheduled_at": iso(now() - timedelta(days=2)), "completed_at": iso(now() - timedelta(days=2))},
    {"id": "s_ghost", "account_id": "a1", "status": "completed",
     "scheduled_at": iso(now() - timedelta(days=2))},  # completed but no record
])
r = agents.bill_service("s_skip")
ok("refused" in r and "ends the account" in r["refused"], "a skipped stop cannot be billed")
ok(not any(a for a in store.load("approvals") if a.get("subject") == "s_skip"),
   "the refused billing never became an approvable row")
r = agents.bill_service("s_ghost")
ok("refused" in r, "completed-without-a-record cannot be billed either")
r = agents.bill_service("s_done")
ok(r.get("executed") and r["rung"] == "R2", "a completed, recorded service bills at R2 and logs")
ok(store.by_id("services", "s_done").get("billed_at"), "…and the billing is recorded")

# ---------------------------------------------------------------- guarantee language
okg, why = core.guarantee_ok("We guarantee your ants will be gone for good — 100% eliminated!")
ok(not okg and "eliminate" in why, "elimination language is refused")
okg, _ = core.guarantee_ok("Covered under your service plan — we retreat at no charge.")
ok(okg, "coverage language passes")
r = agents.draft_outreach("Pests will never come back, permanently eradicated!")
ok("refused" in r, "the outreach path enforces the check")
ok(any(e["detail"].get("action") == "promise_elimination" for e in store.events(kind="refused")),
   "the language refusal is logged")

# ---------------------------------------------------------------- churn floor + reservice floor
store.save("accounts", [
    {"id": "c1", "name": "two", "status": "active", "payment_issue": True},
    {"id": "c2", "name": "one", "status": "active", "payment_issue": True},
    {"id": "c3", "name": "zero", "status": "active"},
])
store.save("services", [
    {"id": "x1", "account_id": "c1", "kind": "reservice",
     "scheduled_at": iso(now() - timedelta(days=10)), "status": "completed",
     "completed_at": iso(now() - timedelta(days=10))},
])
cb = core.churn_board()
ok(cb["n"] == 1 and cb["rows"][0]["account"] == "c1", "two signals make the list")
ok(cb["single_signal"] == 1, "one signal is counted separately")
rr = core.reservice_rate()
ok(rr.get("_missing") and "need 50" in rr["_missing"], "the reservice rate refuses below its floor")

# ---------------------------------------------------------------- R0 probes
for action in ("answer_chemical_safety", "bill_skipped_service", "promise_elimination"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("answer_chemical_safety", "bill_skipped_service", "promise_elimination")
           for a in core.gate.pending()), "no R0 action reached the approval queue")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Reservice-flagged accounts saved"]["value"] is None,
   "the save line is blank without the operator's rate")
ok(labels["Exposure routing"]["kind"] == "scenario" and labels["Exposure routing"]["value"] is None,
   "safety routing is never monetized by us")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("the cat was mouthing one of the granules by the door", "exposure"),
                   ("how long before we can air out the bedroom", "safety_question"),
                   ("don't come back next month, we're switching companies", "cancellation")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:42]} → {want}")

# ---------------------------------------------------------------- drafted copy
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

body = agents._reservice_copy({"text": "ants are back"})
ok("covered under your service plan" in body and "no charge" in body,
   "reservice copy uses coverage language")
okg, _w = core.guarantee_ok(body)
ok(okg, "reservice copy passes the guarantee check structurally")
ok("yourco" not in body.lower(), "white-label: no yourco name in outward copy")

acct9 = {"id": "ac9", "name": "Rivera Household", "status": "active", "payment_issue": True,
         "complaint_open": True}
store.upsert("accounts", acct9)
save = agents._save_visit_copy(acct9)
ok("checking in, not upselling" in save and "free" in save,
   "save-visit copy is a walk, not a pitch")
ok(core.guarantee_ok(save)[0], "save-visit copy passes the guarantee check")

out = agents.save_visit_sweep()
ok(out["drafted"] >= 1, "a two-signal account gets one drafted save visit")
ok(store.by_id("accounts", "ac9").get("save_visit_at"), "the visit window is recorded")
out = agents.save_visit_sweep()
ok(out["drafted"] == 0, "30-day cooldown holds — no second draft")

# ---------------------------------------------------------------- recovered, counted
rec = core.recovered_this_week()
ok(rec["reservices_booked"] == 0 and rec["save_visits_sent"] == 0,
   "nothing sent → zeros, honestly")
store.log_event("draft_reservice_booking", "mg1", "human:frontdesk", "R1", {})
store.log_event("draft_save_visit", "ac9", "human:routemanager", "R1", {})
rec = core.recovered_this_week()
ok(rec["reservices_booked"] == 1 and rec["save_visits_sent"] == 1,
   "human sends are counted; agent drafts are not")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
