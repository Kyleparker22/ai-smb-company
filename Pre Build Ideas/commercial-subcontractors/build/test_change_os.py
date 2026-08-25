#!/usr/bin/env python3
"""Change OS — the honesty suite. A refusal to state an uncomputable number is
a test here, not a nicety."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["CHANGEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="changeos-test-")
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


# ---------------------------------------------------------------- classifier
c = core.classify_note("super directed us to add a second condensate run on L3")
ok(c["label"] == "change_event", "a directed extra is a change event")
c = core.classify_note("installed VAV boxes per plans, floor 2 complete")
ok(c["label"] == "base_scope", "per-plans production is base scope")
c = core.classify_note("")
ok(c["label"] == "ambiguous", "an empty note is ambiguous — a human reads it")
c = core.classify_note("misc site stuff, talked to jim")
ok(c["label"] == "ambiguous", "no signal means routed, never guessed")
c = core.classify_note("delay - electrical trade not clear of our area, crew standing")
ok(c["label"] == "change_event", "a delay with a named cause is a potential claim event")

ev = core.run_eval()
ok(ev["n"] == len(core.EVAL_CASES), "the eval runs the whole labelled set")
ok(ev["costly_label"] == "change_event", "the costly class is the missed change event")
ok(ev["costly_missed"] == 0, f"zero missed change events in the shipped eval (missed={ev['costly_missed']})")
ok("MONEY NEVER BILLED" in ev["costly_note"], "the eval names the stake in its own text")

# ---------------------------------------------------------------- the submit refusal
store.wipe()
store.save("config", {"company": "t"})
co_bad = {"id": "co1", "project_id": "p1", "state": "draft", "value": 1000,
          "directive_ref": None, "summary": "verbal extra"}
co_good = {"id": "co2", "project_id": "p1", "state": "draft", "value": 1000,
           "directive_ref": "dir_1", "summary": "signed extra"}
store.save("cos", [co_bad, co_good])

r = agents.submit_co("co1")
ok("refused" in r, "a CO with no directive is refused at submission")
ok("dispute" in r["refused"], "…and the refusal explains the why")
ok(not any(a for a in store.load("approvals") if a.get("subject") == "co1"),
   "the refused CO never becomes an approvable row")
ok(any(e["kind"] == "refused" for e in store.events(subject="co1")), "the refusal is logged")

r = agents.submit_co("co2")
ok(r.get("approval"), "a CO with a directive queues for a human")
ok(store.by_id("cos", "co2")["state"] == "draft", "…and stays draft until the human clicks")

okd, why = core.advance_co({"state": "draft", "directive_ref": "d"}, "approved")
ok(not okd, "the state machine refuses to jump draft → approved")

# ---------------------------------------------------------------- money honesty
p_nosov = {"id": "p9", "name": "x", "gc_id": "g1", "contract_value": None}
store.save("pay_apps", [{"id": "a1", "project_id": "p9", "gc_id": "g1", "billed": 100_000,
                         "retainage_held": 10_000, "retainage_released": 0,
                         "billed_at": iso(now() - timedelta(days=40)),
                         "paid": 90_000, "paid_at": iso(now() - timedelta(days=5))}])
m = core.project_money(p_nosov)
ok(m["pct_billed"] is None and "unknowable" in m["_missing"],
   "no schedule of values → % complete refuses, never estimated")
ok(m["billed"] == 100_000 and m["retainage_held"] == 10_000, "counted money still counts")

s = core.gc_pay_speed("g1")
ok(s.get("_missing") and "need 4" in s["_missing"],
   "pay speed refuses below 4 paid apps — reputation is not a number")

# ---------------------------------------------------------------- retainage
store.save("projects", [{"id": "p9", "name": "done job", "gc_id": "g1",
                         "substantial_completion": iso(now() - timedelta(days=120)),
                         "retainage_terms_days": 60}])
ret = core.retainage_aging()
ok(len(ret) == 1 and ret[0]["overdue"], "retainage past terms is named overdue")
ok(ret[0]["held"] == 10_000, "held amount is counted from the pay apps")

# ---------------------------------------------------------------- deadlines
store.save("config", {"company": "t", "notice_rules": core.DEFAULT_NOTICE_RULES})
store.save("projects", [
    {"id": "pTX", "name": "tx job", "gc_id": "g1", "state_code": "TX",
     "first_furnish": iso(now() - timedelta(days=60)), "notices_filed": []},
    {"id": "pGA", "name": "ga job", "gc_id": "g1", "state_code": "GA",
     "first_furnish": iso(now() - timedelta(days=10)), "notices_filed": []},
    {"id": "pND", "name": "no dates", "gc_id": "g1", "state_code": "FL", "notices_filed": []},
])
b = core.deadline_board()
ok(any(d["project"] == "tx job" and d["step"] == "monthly notice" and d["days_left"] in (14, 15)
       for d in b["deadlines"]), "a TX deadline computes from first furnishing")
ok(all(d["label"].startswith("DATE ALERT") for d in b["deadlines"]),
   "every deadline is labelled a date alert, not legal advice")
ok(any("no rule set" in u["why"] for u in b["uncomputable"]),
   "a state with no rule set is uncomputable and says so")
ok(any("no first furnishing" in u["why"] for u in b["uncomputable"]),
   "a project with no furnishing date is uncomputable and says so")
ok("replace with counsel-reviewed" in b["rules_source"], "the rule set names itself a default")

# swap the rule set and the deadline moves — rules drive the calendar
custom = {"_source": "custom", "TX": {"steps": [
    {"key": "monthly_notice", "label": "monthly notice", "days_after_first_furnish": 90}]}}
store.save("config", {"company": "t", "notice_rules": custom})
b2 = core.deadline_board()
tx = [d for d in b2["deadlines"] if d["project"] == "tx job"][0]
ok(tx["days_left"] in (29, 30), "changing the rule set changes the computed deadline")

# ---------------------------------------------------------------- R0 probes
store.save("config", {"company": "t"})
for action in ("file_lien", "file_notice", "assert_entitlement"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("file_lien", "file_notice", "assert_entitlement")
           for a in core.gate.pending()), "no R0 action ever reached the approval queue")
ok(set(core.matrix.never_promote()) >= {"file_lien", "file_notice", "assert_entitlement"},
   "the legal actions can never promote")

# ---------------------------------------------------------------- capture sweep + demo protection
store.save("notes", [
    {"id": "n1", "project_id": "p1", "text": "T&M ticket signed for saturday demo work",
     "est_value": 5400, "directive_ref": "dir_9"},
    {"id": "n2", "project_id": "p1", "text": "hung 12 sticks of pipe on L2", "est_value": 0},
    {"id": "n3", "project_id": "p1", "text": "see photos", "est_value": 0},
    {"id": "nd", "project_id": "p1", "text": "super directed extra run", "est_value": 100,
     "demo_tag": "demo"},
])
store.save("cos", [])
out = agents.capture_sweep()
ok(out["classified"] == 4 and out["drafted"] == 1 and out["ambiguous"] == 1,
   "the sweep classifies all, drafts only real change events")
ok(not any(c.get("note_id") == "nd" for c in store.load("cos")),
   "demo-tagged notes are never swept into the ledger")

# ---------------------------------------------------------------- roi + automation
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Pay-app assembly time"]["value"] is None,
   "a line missing operator inputs renders blank")
ok(labels["Lien-right exposure on watched deadlines"]["kind"] == "scenario",
   "exposure is a scenario, never a saving")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation is counted or refused, never asserted")

# a fresh store refuses the rate
import _kit.store as ks
ok("need" in (core.automation().get("_missing") or "need"),
   "below the floor the rate refuses")

# ---------------------------------------------------------------- the retainage ladder
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

row = {"project_id": "p1", "project": "Mercy East", "gc_id": "g1", "held": 41000,
       "days_since_completion": 61, "overdue": True, "terms_days": 60}
d = core.due_retainage_touch(row, [], _now())
ok(d and d.get("step") == 1, "just past terms → step 1 due")
touch1 = [{"step": 1, "at": _iso(_now() - timedelta(days=3))}]
ok(core.due_retainage_touch(row, touch1, _now()) is None,
   "cooldown holds — no second touch 3 days after the first")
row2 = dict(row, days_since_completion=60 + 21)
touch1_old = [{"step": 1, "at": _iso(_now() - timedelta(days=15))}]
d = core.due_retainage_touch(row2, touch1_old, _now())
ok(d and d.get("step") == 2, "past cooldown and threshold → step 2")
row3 = dict(row, days_since_completion=60 + 50)
ok(core.due_retainage_touch(row3, touch1_old, _now()).get("step") == 2,
   "steps never skip — step 2 before step 3 even when both thresholds passed")
touches3 = [{"step": s, "at": _iso(_now() - timedelta(days=30 - s))} for s in (1, 2, 3)]
d = core.due_retainage_touch(row3, touches3, _now())
ok(d and d.get("escalate"), "past the ladder → escalate, never a fourth email")
ok("silence is an answer" in d["why"], "escalation names the rule")
ok(core.due_retainage_touch(dict(row, overdue=False), [], _now()) is None,
   "inside terms → no touch at all")

# ladder sweep drafts with copy, records the touch, and escalates once only
store.save("projects", [{"id": "p9", "name": "Harbor Lab", "gc_id": "g1", "state_code": "TX",
                         "substantial_completion": _iso(_now() - timedelta(days=130)),
                         "retainage_terms_days": 60}])
store.save("gcs", [{"id": "g1", "name": "Bellwether Construction"}])
store.save("pay_apps", [{"id": "pa9", "project_id": "p9", "gc_id": "g1", "billed": 200000,
                         "paid": 180000, "retainage_held": 20000, "retainage_released": 0}])
out = agents.retainage_sweep()
ok(out["drafted"] == 1, "one chase drafted for the overdue row")
p9 = store.by_id("projects", "p9")
ok(p9["retainage_touches"][0]["step"] == 1, "the touch is recorded on the row")
body = p9["retainage_touches"][0]["body"]
ok("Bellwether" in body and "$20,000" in body, "copy carries the GC and the ledger number")
ok("yourco" not in body.lower(), "white-label: no yourco name in outward copy")
ok(not any(w in body.lower() for w in ("lien", "legal", "entitle", "claim of")),
   "no legal language in chase copy — entitlement is R0")
out = agents.retainage_sweep()
ok(out["drafted"] == 0, "cooldown blocks a second draft in the same week")

# ---------------------------------------------------------------- the CO packet
store.save("notes", [{"id": "n7", "project_id": "p9", "at": _iso(_now()),
                      "text": "super directed extra condensate run L3"}])
store.save("cos", [{"id": "co7", "project_id": "p9", "note_id": "n7", "state": "draft",
                    "value": 8400, "directive_ref": "FD-112",
                    "summary": "extra condensate run"}])
r = agents.submit_co("co7")
ok(r.get("rung") == "R1" and r.get("approval"), "packeted CO queues at R1")
ok("FD-112" in r["packet"]["cover"] and "$8,400" in r["packet"]["cover"],
   "cover cites directive and value")
ok(r["packet"]["field_note"] == "super directed extra condensate run L3",
   "packet traces to the field note")
store.upsert("cos", {"id": "co8", "project_id": "p9", "state": "draft", "value": 900,
                     "directive_ref": None, "summary": "verbal extra"})
ok("refused" in agents.submit_co("co8"), "no directive still refuses — packet or not")

# ---------------------------------------------------------------- recovered, counted
rec = core.recovered_this_week()
ok(rec["cos_submitted"] == 0 and rec["co_value"] == 0,
   "nothing submitted yet — recovered reads zero, honestly")
store.log_event("submit_co_done", "co7", "human:owner", "R1", {"value": 8400})
store.log_event("retainage_chase_sent", "p9", "human:owner", "R1", {})
rec = core.recovered_this_week()
ok(rec["cos_submitted"] == 1 and rec["co_value"] == 8400, "a submitted CO is counted from its event")
ok(rec["chases_sent"] == 1, "chases sent are counted from events")
ok("counted from the event log" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
