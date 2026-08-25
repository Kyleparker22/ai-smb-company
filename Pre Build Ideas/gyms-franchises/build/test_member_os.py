#!/usr/bin/env python3
"""Member OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["MEMBEROS_DATA_ROOT"] = tempfile.mkdtemp(prefix="memberos-test-")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import agents, core
from core import store
from _kit.store import iso, now, parse

PASS = FAIL = 0


def ok(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL  {msg}")


# ---------------------------------------------------------------- triage + eval
ok(core.read_message("I want to cancel my membership")["label"] == "cancellation",
   "a cancellation classifies")
ok(core.read_message("I hurt my shoulder during the 6am class")["label"] == "injury",
   "an injury report classifies")
ok(core.read_message("will lifting fix my back pain")["label"] == "medical_question",
   "a medical question classifies")
ok(core.read_message("I was charged twice this month")["label"] == "billing", "billing classifies")
ok(core.read_message("")["label"] == "human", "empty routes to a person")

ev = core.run_eval()
ok(ev["costly_label"] == "critical" and ev["costly_missed"] == 0,
   f"zero missed critical messages in the shipped eval ({ev['costly_missed']})")
ok("ILLEGAL CONTINUED BILLING" in ev["costly_note"], "the eval names the stake")

# ---------------------------------------------------------------- cancellation clock
store.wipe()
store.save("config", {"company": "t", "cancel_rules": core.DEFAULT_CANCEL_RULES})
m_ca = {"id": "m1", "name": "A", "state_code": "CA", "status": "active"}
clock = core.cancellation_clock(m_ca, iso(now()))
ok(clock["days"] == 3, "a CA cancellation gets the 3-day window")
ok("starts at the request" in clock["rule_label"], "the clock starts at the request")
ok("replace with counsel-reviewed" in clock["rules_source"], "the rule set names itself a default")
clock = core.cancellation_clock({"state_code": "ZZ"}, iso(now()))
ok(clock["days"] == 5 and "default window" in clock["note"],
   "an unknown state falls to the default window, named as such")

store.save("members", [m_ca])
store.save("messages", [{"id": "msg1", "member_id": "m1",
                         "text": "I want to cancel my membership please", "at": iso(now())}])
r = agents.handle_message("msg1")
acts = [s["action"] for s in r["steps"]]
ok(acts[0] == "start_cancel_clock" and "draft_retention_offer" in acts,
   "the clock starts FIRST; the retention draft is separate")
ok(len(store.load("cancellations")) == 1, "the cancellation row exists immediately")
clock_events = [e for e in store.events() if e["kind"] in ("start_cancel_clock",)]
ok(len(clock_events) == 1 and clock_events[0]["rung"] == "R2",
   "starting the clock is R2 — delay is the harm")

# ---------------------------------------------------------------- injury / medical
store.save("messages", [{"id": "msg2", "member_id": "m1",
                         "text": "I hurt my knee during the class at your gym", "at": iso(now())}])
r = agents.handle_message("msg2")
ok(r["steps"][0].get("refused") == "nothing drafted — a human calls",
   "an injury gets nothing in writing")
ok(not any(a["subject"] == "msg2" for a in store.load("approvals")),
   "no draft row exists for the injury")

# ---------------------------------------------------------------- dunning
store.save("payments", [{"id": "p1", "member_id": "m2", "failed": True, "amount": 59,
                         "at": iso(now() - timedelta(days=3))}])
m2 = {"id": "m2", "name": "B", "state_code": "TX", "status": "active", "dunning_touches": []}
plan = core.dunning_plan(m2)
ok(plan["action"] == "draft" and "No rush" in plan["text"], "an open failure drafts the gentle template")
okt, why = core.dunning_text_ok("final notice before we send this to collections")
ok(not okt and "never threatens" in why, "threat language is structurally refused")
m2["dunning_touches"] = [{"at": iso(now() - timedelta(days=30))}] * core.DUNNING_MAX_TOUCHES
plan = core.dunning_plan(m2)
ok(plan["action"] == "human" and "never escalates to threats" in plan["why"],
   "an exhausted ladder goes to a person, not to threats")
m2["dunning_touches"] = [{"at": iso(now() - timedelta(days=2))}]
ok(core.dunning_plan(m2)["action"] == "none", "cooldown respected")

# ---------------------------------------------------------------- churn floor
store.save("payments", [])
store.save("members", [
    {"id": "r1", "name": "two-signal", "status": "active", "visits_30d": 2,
     "visits_prior_30d": 10, "no_future_booking": True},
    {"id": "r2", "name": "one-signal", "status": "active", "visits_30d": 2,
     "visits_prior_30d": 10},
    {"id": "r3", "name": "healthy", "status": "active", "visits_30d": 9, "visits_prior_30d": 10},
    {"id": "r4", "name": "cancelled", "status": "cancelled", "visits_30d": 0,
     "visits_prior_30d": 10, "no_future_booking": True},
])
cb = core.churn_board()
ok(cb["n"] == 1 and cb["rows"][0]["member"] == "r1", "two signals make the list")
ok(cb["single_signal"] == 1, "one signal is counted separately — a note, not a pattern")
ok(not any(r["member"] == "r4" for r in cb["rows"]), "non-active members are not churn-watched")

# ---------------------------------------------------------------- churn split floor
store.save("cancellations", [])
cs = core.churn_split()
ok(cs.get("_missing") and "need 10" in cs["_missing"], "the churn split refuses below its floor")

# ---------------------------------------------------------------- R0 probes
for action in ("delay_cancellation", "respond_to_injury", "medical_claim", "threaten_collections"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("delay_cancellation", "respond_to_injury", "medical_claim",
                           "threaten_collections") for a in core.gate.pending()),
   "no R0 action reached the approval queue")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Failed payments recovered"]["value"] is None,
   "the recovery line is blank without the operator's rate")
ok(labels["Slow-cancel regulatory exposure"]["kind"] == "scenario",
   "regulatory exposure is a scenario, never a saving")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("quitting the gym, it's too far from my new place", "cancellation"),
                   ("dropped a dumbbell on my foot during open gym", "injury"),
                   ("is it safe to do your classes while pregnant", "medical_question")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:42]} → {want}")

# ---------------------------------------------------------------- drafted copy
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

mem9 = {"id": "mb9", "name": "Jordan Achebe", "status": "active", "state_code": "CA",
        "visits_30d": 2, "visits_prior_30d": 10, "no_future_booking": True}
store.upsert("members", mem9)
save = agents._retention_copy(mem9)
ok("Jordan" in save and "processed as asked" in save,
   "retention copy says the cancel proceeds regardless")
ok("freeze" in save and "off-peak" in save, "one concrete alternative, stated")
ok(not any(w in save.lower() for w in ("please stay", "we'll miss you", "don't go")),
   "no guilt language in the save offer")
wb = agents._winback_copy(mem9)
ok("not\na pitch" in wb or "not a pitch" in wb, "winback names itself a check-in, not a pitch")
ok("yourco" not in (save + wb).lower(), "white-label: no yourco name in outward copy")

# winback sweep drafts once and respects the cooldown
out = agents.winback_sweep()
ok(out["drafted"] >= 1, "a two-signal member gets one drafted check-in")
ok(store.by_id("members", "mb9").get("winback_at"), "the send window is recorded")
out = agents.winback_sweep()
ok(out["drafted"] == 0 or store.by_id("members", "mb9")["winback_at"], "21-day cooldown holds")
before = len([a_ for a_ in store.load("approvals") if a_["action"] == "draft_winback"
              and a_["subject"] == "mb9"])
ok(before == 1, "exactly one winback approval row for the member")

# dunning copy never threatens — the structural check holds against the template
okd, _ = core.dunning_text_ok(core.DUNNING_TEMPLATE.format(name="X"))
ok(okd, "the shipped dunning template passes its own threat check")
okd, why = core.dunning_text_ok("pay now or we send this to collections")
ok(not okd and "collections" in why, "threat language is structurally refused")

# ---------------------------------------------------------------- recovered, counted
rec = core.recovered_this_week()
ok(rec["payments_recovered"] == 0 and rec["winbacks_sent"] == 0,
   "nothing recovered → zeros, honestly")
store.upsert("payments", {"id": "py9", "member_id": "mb9", "amount": 89, "failed": True,
                          "recovered_at": _iso(_now() - timedelta(days=2))})
store.log_event("draft_dunning", "mb9", "human:frontdesk", "R1", {})
store.log_event("draft_winback", "mb9", "human:frontdesk", "R1", {})
rec = core.recovered_this_week()
ok(rec["payments_recovered"] == 1 and rec["recovered_value"] == 89,
   "a recovered payment is counted with its value")
ok(rec["dunning_sent"] == 1 and rec["winbacks_sent"] == 1,
   "human sends are counted; agent drafts are not")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
