#!/usr/bin/env python3
"""Unit OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["UNITOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="unitos-test-")
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


# ---------------------------------------------------------------- triage
ok(core.read_message("I got food poisoning from your carnitas")["label"] == "illness",
   "an illness claim classifies")
ok(core.read_message("my daughter had an allergic reaction, we used her epipen")["label"] == "allergen_incident",
   "an allergen incident classifies")
ok(core.read_message("is the mole gluten free? my son has celiac")["label"] == "allergen_question",
   "an allergen QUESTION is its own dangerous class")
ok(core.read_message("health inspector left a notice today")["label"] == "health_dept",
   "health-department contact classifies")
ok(core.read_message("my burrito was cold and the wait was 40 minutes")["label"] == "complaint",
   "a service complaint classifies")
ok(core.read_message("")["label"] == "human", "empty routes to a person")

ev = core.run_eval()
ok(ev["costly_label"] == "dangerous" and ev["costly_missed"] == 0,
   f"zero missed dangerous messages in the shipped eval ({ev['costly_missed']})")
ok("ADMISSION" in ev["costly_note"], "the eval names the stake")

# ---------------------------------------------------------------- handling
store.wipe()
store.save("config", {"company": "t"})
store.save("messages", [
    {"id": "m_ill", "unit_id": "u1", "text": "I got food poisoning from your carnitas"},
    {"id": "m_q", "unit_id": "u1", "text": "do the tortillas contain nuts"},
    {"id": "m_c", "unit_id": "u1", "text": "order was wrong, missing the guac we paid for"},
])
r = agents.handle_message("m_ill")
ok(r["steps"][0].get("refused") and "nothing in writing" in r["steps"][0]["refused"],
   "an illness claim gets NO drafted reply")
ok(any(e["kind"] == "refused" and e["detail"]["action"] == "respond_to_illness_claim"
       for e in store.events(subject="m_ill")), "the illness refusal is logged with its action")
ok(not any(a["subject"] == "m_ill" and a["action"].startswith("draft")
           for a in store.load("approvals")), "no reply draft exists for the illness claim")

r = agents.handle_message("m_q")
ok(any(e["detail"].get("action") == "answer_allergen_question"
       for e in store.events(kind="refused", subject="m_q")),
   "an allergen question is refused, not answered")

r = agents.handle_message("m_c")
ok(any(a["subject"] == "m_c" and a["action"] == "draft_complaint_reply"
       for a in store.load("approvals")), "a routine complaint drafts at R1")

# ---------------------------------------------------------------- variance
p_ok = {"unit_id": "u1", "counts_taken": True, "sales": 100_000,
        "theoretical_cost": 28_000, "actual_cost": 31_000}
v = core.variance(p_ok)
ok(v["variance_pp"] == 3.0 and v["flagged"], "a 3pp variance computes and flags")
ok(v["dollars"] == 3000, "the dollar gap is counted")
v = core.variance({"unit_id": "u2", "counts_taken": False, "sales": 100_000})
ok(v.get("_missing") and "last month's number is not this month's" in v["_missing"],
   "no counts → no number, with the reason")
v = core.variance({"unit_id": "u3", "counts_taken": True, "sales": 0})
ok(v.get("_missing"), "no sales → refused")

store.save("units", [{"id": "u1", "name": "A"}, {"id": "u2", "name": "B"},
                     {"id": "u3", "name": "C — no periods"}])
store.save("periods", [dict(p_ok, id="p1", period="2026-07"),
                       {"id": "p2", "unit_id": "u2", "period": "2026-07", "counts_taken": False,
                        "sales": 90_000}])
vb = {r["unit"]: r for r in core.variance_board()}
ok(vb["A"]["flagged"], "the board flags the over-threshold unit")
ok(vb["B"].get("_missing"), "the no-counts unit reads unmeasured on the board")
ok(vb["C — no periods"].get("_missing"), "a unit with no periods reads unmeasured")

# ---------------------------------------------------------------- R0 probes
for action in ("respond_to_illness_claim", "answer_allergen_question",
               "respond_to_health_department", "estimate_variance"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("respond_to_illness_claim", "answer_allergen_question",
                           "respond_to_health_department", "estimate_variance")
           for a in core.gate.pending()), "no R0 action reached the approval queue")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Variance points recovered"]["value"] is None,
   "the variance line is blank without the operator's recovery share")
ok(labels["Illness-claim exposure"]["kind"] == "scenario",
   "claim exposure is a scenario, never a saving")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("are the churros fried in the same oil as the shrimp", "allergen_question"),
                   ("whole table was throwing up after the party platter", "illness"),
                   ("inspection notice taped to the door at the elm street store", "health_dept")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

# ---------------------------------------------------------------- drafted copy
store.save("units", [{"id": "u9", "name": "Elm Street"}])
m9 = {"id": "mg9", "unit_id": "u9", "text": "my burrito was cold and the wait was 40 minutes"}
store.upsert("messages", m9)
body = agents._complaint_reply_copy(m9)
ok("Elm Street" in body and "on us" in body, "reply owns the failure and offers the make-right")
ok("sorry" in body.lower(), "the apology is plain — principle 11 covers prices, not failures")
ok(not any(w in body.lower() for w in ("allerg", "illness", "sick", "health")),
   "complaint copy never wanders into health territory")
ok("yourco" not in body.lower(), "white-label: no yourco name in outward copy")
out = agents.handle_message("mg9")
ok(store.by_id("messages", "mg9").get("draft_reply"), "the draft is recorded on the message")

# ---------------------------------------------------------------- the variance brief
store.save("periods", [{"id": "pd9", "unit_id": "u9", "period": "2026-07", "counts_taken": True,
                        "sales": 210000, "actual_cost": 70000, "theoretical_cost": 63000}])
b = agents.open_variance_brief("u9")
ok(b["brief"] and len(b["brief"]) == 5, "a flagged unit gets the five-question walk")
ok(all(q.strip().endswith("?") or "(" in q for q in b["brief"]),
   "the brief asks questions — it never concludes")
ok("never a thief" in b["rule"], "the brief states the attribution rule")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "attribute_variance_cause"
       for e in store.events()), "opening a brief logs the cause-attribution refusal")
store.save("periods", [{"id": "pd10", "unit_id": "u9", "period": "2026-08", "counts_taken": False}])
b = agents.open_variance_brief("u9")
ok(b["brief"] is None and "confident fiction" in b["note"],
   "no counts → no brief, and the reason says why")

# ---------------------------------------------------------------- recovered, counted
rec = core.recovered_this_week()
ok(rec["replies_sent"] == 0, "nothing sent → zero, honestly")
store.log_event("draft_complaint_reply", "mg9", "human:manager", "R1", {"approval": "apz"})
rec = core.recovered_this_week()
ok(rec["replies_sent"] == 1 and rec["briefs_opened"] == 1,
   "human sends and opened briefs are counted from the log")
ok(rec["dangerous_escalated"] >= 1, "dangerous escalations are counted")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
