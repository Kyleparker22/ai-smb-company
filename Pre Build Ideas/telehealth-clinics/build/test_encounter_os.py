#!/usr/bin/env python3
"""Encounter OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["ENCOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="encos-test-")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import agents, core, seed
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


seed.build(n_patients=160)

# ---------------------------------------------------------------- licensure is structural
covered = {"FL", "GA", "TX", "NC", "SC", "TN", "AZ", "OH"}
for st in covered:
    ok(len(core.eligible_clinicians(st)) > 0, f"a covered state ({st}) has candidates")
for st in ("CA", "CO", "IL", "WA", "PA"):
    ok(core.eligible_clinicians(st) == [], f"an uncovered state ({st}) has no candidate at all")

# NY is the trap: a clinician IS licensed there, but is inactive.
ny = [c for c in store.load("clinicians") if "NY" in (c.get("licences") or [])]
ok(len(ny) == 1 and ny[0]["active"] is False, "the seed contains an inactive NY licence")
ok(core.eligible_clinicians("NY") == [], "an INACTIVE licence never counts as coverage")

# every candidate returned is genuinely licensed — the load-bearing invariant
for st in covered:
    for c in core.eligible_clinicians(st):
        ok(st in c["licences"] and c["active"],
           f"every candidate for {st} is active and licensed there")

# routing refuses rather than degrading
p_bad = next(p for p in store.load("patients") if p["state"] not in covered)
r = core.route(p_bad["id"])
ok(r.get("refused"), "routing into an uncovered state refuses")
ok(r["coverage_gap"] is True, "the refusal is labelled a coverage gap")
ok("no 'closest match' fallback" in r["why"], "the refusal says there is no fallback, on purpose")
ok("candidates" not in r, "a refusal offers no candidates whatsoever")
ok("licensing decision for the clinic" in r["action"], "it names whose decision this is")

p_ok = next(p for p in store.load("patients") if p["state"] in covered)
r = core.route(p_ok["id"])
ok(r.get("candidates"), "routing inside a covered state produces candidates")
ok(all(p_ok["state"] in (store.by_id("clinicians", c["clinician"]) or {}).get("licences", [])
       for c in r["candidates"]), "every routed candidate holds that state's licence")
ok(r["note"].startswith("only clinicians licensed in"), "the result states what it considered")
loads = [c["open_encounters"] for c in r["candidates"]]
ok(loads == sorted(loads), "candidates are ordered by who has capacity")

# no state recorded → refuse, never guess
store.upsert("patients", {"id": "ptNOSTATE", "name": "No State", "state": "", "joined": iso(now())})
r = core.route("ptNOSTATE")
ok(r.get("refused") == "the patient's state is not recorded", "a missing state refuses")
ok("guessed never" in r["why"], "it says the location is never guessed")

ok(core.matrix.rung_for("route_unlicensed")["rung"] == "R0", "unlicensed routing is R0")
ok("route_unlicensed" in core.matrix.never_promote(), "it can never be promoted")
ok(core.matrix.promotable("route_unlicensed", streak=99999)["promote"] is False,
   "no streak ever promotes unlicensed routing")

# ---------------------------------------------------------------- coverage gaps
gaps = core.coverage_gaps()
ok(len(gaps) > 0, "coverage gaps are surfaced")
ok(all(core.eligible_clinicians(g["state"]) == [] for g in gaps),
   "every reported gap really has no licensed clinician")
ok(all(g["patients"] > 0 for g in gaps), "a gap is only reported where patients actually are")
ok(not any(g["state"] in covered for g in gaps), "no covered state is reported as a gap")

# ---------------------------------------------------------------- async triage
for text, kind in [("I've had chest pain since this morning", "cardiac"),
                   ("I can't breathe properly", "breathing"),
                   ("I've been thinking about hurting myself", "self_harm"),
                   ("my speech went slurred an hour ago", "neuro"),
                   ("I'm pregnant and having severe pain", "obstetric")]:
    c = core.read_intake(text)
    ok(c["label"] == "urgent", f"'{text[:30]}…' is urgent")
    ok(c["kind"] == kind, f"'{text[:30]}…' types as {kind}")
ok(core.read_intake("Looking to continue my program, no problems so far.")["label"] == "routable",
   "a routine narrative is routable")

urgent_intake = {"id": "inURG", "patient": p_ok["id"], "at": iso(now()),
                 "narrative": "I've been thinking about hurting myself",
                 "answers": {"chief_complaint": "x"}, "triaged_at": None, "label": None}
store.upsert("intakes", urgent_intake)
r = agents.triage_intake("inURG")
ok(r["stopped"] is True, "an urgent intake stops the async flow")
ok(r["kind"] == "self_harm", "the stop names what it saw")
ok(core.URGENT_INSTRUCTION in r["said"], "the emergency instruction is said verbatim")
ok("chart" not in r, "no chart is prepared for an urgent intake")
ok("nothing was assessed" in r["why"], "it states that nothing was assessed")

# a chart names its gaps rather than presenting holes
store.upsert("intakes", {"id": "inGAP", "patient": p_ok["id"], "at": iso(now()),
                         "narrative": "routine follow up",
                         "answers": {"chief_complaint": "refill"}, "triaged_at": None, "label": None})
c = core.prepare_chart("inGAP")
ok(c["complete"] is False, "a chart with unanswered questions is not complete")
ok("duration" in c["missing"] and "allergies" in c["missing"], "every unanswered field is named")
ok(c["chart"]["allergies"] is None, "an unanswered field is None, never invented")

# ---------------------------------------------------------------- documentation is a hard stop
e = {"id": "eTEST", "patient": p_ok["id"], "clinician": "cl1", "paid_at": iso(now()),
     "amount": 99, "started_at": iso(now()), "documentation": {"chief_complaint": True},
     "closed_at": None, "closed_by": None}
store.upsert("encounters", e)
r = core.close_encounter("eTEST", "clinician")
ok(r.get("refused") == "the encounter is not fully documented", "an undocumented encounter cannot close")
ok(len(r["missing"]) == len(core.REQUIRED_DOC) - 1, "every missing element is named")
ok(store.by_id("encounters", "eTEST")["closed_at"] is None, "it really did not close")
ok("survives a complaint" in r["why"], "the refusal says why the note matters")

e["documentation"] = {k: True for k in core.REQUIRED_DOC}
store.upsert("encounters", e)
r = core.close_encounter("eTEST", "clinician")
ok(r.get("closed_by") == "clinician", "a fully documented encounter closes")
ok(store.by_id("encounters", "eTEST")["closed_at"] is not None, "the close is recorded")

ok(core.matrix.rung_for("close_undocumented")["rung"] == "R0", "closing undocumented is R0")
ok("close_undocumented" in core.matrix.never_promote(), "and never promotable")
before = len(core.gate.pending())
res = core.gate.act("close_undocumented", "charting", "eTEST", {})
ok(res.get("refused") is True, "it is refused outright")
ok(len(core.gate.pending()) == before, "an R0 never becomes a clickable approval")

# ---------------------------------------------------------------- clinical refusal
r = agents.answer_clinical("is this dose safe?")
ok(r["refused"] is True, "a clinical question is refused")
ok("can't answer clinical questions" in r["reply"], "the refusal is said to the patient")
ok(core.URGENT_INSTRUCTION in r["reply"], "it still carries the emergency instruction")
ok(core.matrix.rung_for("clinical_advice")["rung"] == "R0", "clinical advice is R0")

# ---------------------------------------------------------------- the leak
unseen = core.paid_not_seen()
ok(all(store.by_id("encounters", u["encounter"]).get("started_at") is None for u in unseen),
   "every 'paid not seen' row really was never started")
ok(all(u["days_since_paid"] >= 3 for u in unseen), "the list respects its own threshold")
d = agents.draft_reengagement(unseen[0]["encounter"]) if unseen else {}
if unseen:
    ok("draft" in d and d["rung"] == "R1", "a re-engagement draft sits at the approval gate")
    for w in ("dose", "diagnos", "treat"):
        ok(w not in d["draft"].lower(), f"the draft contains no '{w}'")

conv = core.conversion()
ok("_missing" in conv or 0.0 <= conv["rate"] <= 1.0, "conversion is a fraction or a refusal")

# ---------------------------------------------------------------- eval
ev = core.run_eval()
ok(ev["costly_label"] == "unlicensed", "the costly class is an unlicensed route")
ok(ev["costly_missed"] == 0, "no unlicensed state is called routable")
ok(ev["costly_recall"] == 1.0, "every unlicensed case is caught")
ok("closes a telehealth clinic" in ev["costly_note"].lower(), "the eval names what the failure costs")

# ---------------------------------------------------------------- numbers refuse
store.save("encounters", [])
c = core.conversion()
ok("_missing" in c and c["rate"] is None, "conversion refuses on an empty book, never 0")

seed.build(n_patients=160)
r = core.roi({})
ok(any(l.get("value") is None for l in r["lines"]), "ROI blanks without operator inputs")
scen = [l for l in r["lines"] if l["kind"] == "scenario"]
ok(len(scen) == 2, "there are two scenario lines")
ok(any("cannot be counted" in (s.get("assumption") or "") for s in scen),
   "prevented exposure is explicitly not counted")
ts = [l for l in r["lines"] if l["kind"] == "time_saved"]
ok(any("not an arithmetic one" in (t.get("note") or "") for t in ts),
   "returned clinician minutes are not silently converted into revenue")
r2 = core.roi({"exposure_value": "40000", "coverage_value": "10000"})
ok(r2["totals"]["scenario"]["total"] == 50000, "scenario lines total together")
ok(r2["totals"]["revenue"]["total"] != 50000, "a scenario never becomes revenue")

au = core.automation()
ok("rate" in au or "_missing" in au, "automation is counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
