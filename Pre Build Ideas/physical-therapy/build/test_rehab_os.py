#!/usr/bin/env python3
"""Rehab OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["REHABOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="rehabos-test-")
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
for text, kind in [("I can't control my bladder since this morning", "cauda_equina"),
                   ("my calf is swollen and hot since yesterday", "dvt"),
                   ("had chest tightness during the exercises", "cardiac"),
                   ("my foot went numb and I'm dragging it", "neuro"),
                   ("fever since my surgery and the incision looks red", "infection")]:
    c = core.read_message(text)
    ok(c["label"] == "red_flag" and c["kind"] == kind, f"red flag typed as {kind}")
    ok(c["instruction"] == core.ER_INSTRUCTION, f"{kind} carries the ER instruction")

ok(core.read_message("should I push through the pain")["label"] == "clinical",
   "a push-through question is clinical")
ok(core.read_message("can't make my appointment tomorrow")["label"] == "cancellation",
   "a cancellation classifies")
ok(core.read_message("")["label"] == "human", "empty routes to a person")

ev = core.run_eval()
ok(ev["costly_label"] == "red_flag" and ev["costly_missed"] == 0,
   f"zero missed red flags in the shipped eval ({ev['costly_missed']})")
ok("PERMANENT DAMAGE" in ev["costly_note"], "the eval names the stake")

# clinical goes unanswered
store.wipe()
store.save("config", {"company": "t"})
store.save("messages", [{"id": "m1", "text": "is it normal to be this sore two days after"}])
r = agents.handle_message("m1")
ok(r["steps"][0].get("refused") == "routed unanswered", "clinical routes unanswered")
ok(any(e["detail"].get("action") == "clinical_answer"
       for e in store.events(kind="refused", subject="m1")), "the refusal is logged")

# ---------------------------------------------------------------- authorization
store.save("visits", [{"id": f"v{i}", "patient_id": "p1", "attended_at": iso()} for i in range(8)])
p_over = {"id": "p1", "authorized_visits": 8}
s = core.auth_state(p_over)
ok(s["over"] and s["remaining"] == 0, "8 of 8 used is over")
okb, why = core.can_book_billable(p_over)
ok(not okb and "audit finding" in why, "booking past auth is refused with the stake named")
p_noauth = {"id": "p2", "authorized_visits": None}
s = core.auth_state(p_noauth)
ok(s.get("_missing") and "never assumed unlimited" in s["_missing"],
   "no auth recorded → unknowable, never unlimited")
okb, why = core.can_book_billable(p_noauth)
ok(not okb and "verifies with the payer" in why, "no-auth booking refused to the payer")
p_ok = {"id": "p3", "authorized_visits": 12}
okb, why = core.can_book_billable(p_ok)
ok(okb, "within auth may book (R1)")

r = agents.book_visit("p9")
ok("error" in r, "unknown patient errors")
store.save("patients", [dict(p_over, name="A", status="active"),
                        dict(p_ok, name="C", status="active")])
r = agents.book_visit("p1")
ok("refused" in r and "never silently booked" in r["note"],
   "the over-auth booking is refused AND queued for the payer")
r = agents.book_visit("p3")
ok(r.get("approval"), "the within-auth booking drafts at R1")

# recert alert
s = core.auth_state({"id": "p4", "authorized_visits": 10,
                     "recert_due": iso(now() + timedelta(days=6))})
ok(s.get("recert_days_left") in (5, 6) and "DATE ALERT" in s["recert_label"],
   "a recert date is a date alert")

# ---------------------------------------------------------------- dropout floor
store.save("patients", [
    {"id": "d1", "name": "two", "status": "active", "visits_prescribed": 12,
     "visits_per_week": 2, "poc_started": iso(now() - timedelta(days=40))},
    {"id": "d2", "name": "one", "status": "active"},
    {"id": "d3", "name": "fine", "status": "active"},
])
store.save("visits", [
    {"id": "w1", "patient_id": "d1", "attended_at": iso(now() - timedelta(days=20))},
    {"id": "w2", "patient_id": "d1", "no_show": True},
    {"id": "w3", "patient_id": "d1", "no_show": True},
    {"id": "w4", "patient_id": "d2", "no_show": True},
    {"id": "w5", "patient_id": "d2", "no_show": True},
])
db = core.dropout_board()
ok(db["n"] == 1 and db["rows"][0]["patient"] == "d1",
   "two-plus signals make the list (gap + no-shows + behind plan)")
ok(db["single_signal"] == 1, "one signal is counted separately")

# ---------------------------------------------------------------- R0 probes
for action in ("clinical_answer", "modify_plan_of_care", "bill_beyond_authorization",
               "promise_outcome"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("clinical_answer", "modify_plan_of_care",
                           "bill_beyond_authorization", "promise_outcome")
           for a in core.gate.pending()), "no R0 action reached the approval queue")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Dropouts brought back"]["value"] is None,
   "the dropout line is blank without the operator's rate")
ok(labels["Red-flag routing"]["kind"] == "scenario", "red-flag routing is never monetized")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want, kind in (
        ("both legs feel weak and pins and needles below the waist", "red_flag", "neuro"),
        ("short of breath going up stairs since the last visit", "red_flag", "cardiac"),
        ("how many reps of the bridges should I do at home", "clinical", None),
        ("running late, can we push my slot 30 minutes", "scheduling", None),
        ("gotta cancel friday, work thing came up", "cancellation", None)):
    r = core.read_message(text)
    ok(r["label"] == want and (kind is None or r.get("kind") == kind),
       f"triage: {text[:42]} → {want}")

# ---------------------------------------------------------------- drafted copy
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

p9 = {"id": "pt9", "name": "Rosa Delgado", "status": "active"}
store.upsert("patients", p9)
body = agents._outreach_copy(p9, {"name": "Rosa Delgado", "signals": []})
ok("Rosa" in body and "check\nin, not chase" in body or "check in, not chase" in body,
   "outreach copy is a check-in, not a chase")
ok("all three are fixable" in body, "the copy names the fixable causes")
ok(not any(w in body.lower() for w in ("recover", "heal", "cure", "outcome", "guarantee")),
   "no outcome promise in outreach copy — promise_outcome is R0")
ok("yourco" not in body.lower(), "white-label: no yourco name in outward copy")
rb = agents._rebook_copy({})
ok("rhythm" in rb and "hold one" in rb, "rebook copy keeps it practical")

# ---------------------------------------------------------------- recovered, counted
base = core.recovered_this_week()
store.log_event("draft_dropout_outreach", "pt9", "human:carecoach", "R1", {})
store.log_event("book_within_auth", "pt9", "human:scheduler", "R1", {})
p9["reauthorized_at"] = _iso(_now() - timedelta(days=1))
store.upsert("patients", p9)
rec = core.recovered_this_week()
ok(rec["outreach_sent"] == base["outreach_sent"] + 1
   and rec["visits_booked"] == base["visits_booked"] + 1,
   "human sends and bookings are counted; agent drafts are not")
ok(rec["reauthorizations"] == base["reauthorizations"] + 1,
   "reauthorizations are counted from the charts")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
