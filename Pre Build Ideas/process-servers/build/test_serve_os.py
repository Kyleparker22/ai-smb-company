#!/usr/bin/env python3
"""Serve OS — the suite. `python3 test_serve_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["SERVEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="serveos_test_")
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
serves = store.load("serves")
ok(len(serves) >= 420, "serves seeded")
ok(sum(1 for s in serves if s["status"] in ("papers_in", "attempting")) >= 300, "~300 open serves")
ok(len(store.load("servers")) == 6, "6 servers")
ok(len(core.diligence_rules()["counties"]) == 3, "3 counties with recorded rules")
ok(core.diligence_rules()["counties"]["Hardin"] != core.diligence_rules()["counties"]["Bellamy"],
   "county rules differ")

print("== triage: the deadline risk reads first ==")
for c in core.EVAL_CASES:
    ok(core.read_message(c["input"])["label"] == c["label"],
       f"triage: {c['input'][:46]!r} → {c['label']}")

print("== the attempt log is append-only ==")
ok(not hasattr(core, "edit_attempt"), "edit_attempt does not exist")
ok(not hasattr(agents, "edit_attempt"), "no edit path in agents either")
n0 = len(store.load("attempts"))
a1 = core.record_attempt("sv_000", "srv_dre", "no answer", "1412 Larkspur Ave, Hardin County")
ok(len(store.load("attempts")) == n0 + 1, "record appends")
ok(a1["late_recorded"] is False, "an attempt recorded at the attempt is not late")
c1 = core.correct_attempt(a1["id"], "srv_dre", outcome="refused to open the door")
ok(c1["supersedes"] == a1["id"], "a correction is a NEW entry pointing at the old")
ok(store.by_id("attempts", a1["id"])["outcome"] == "no answer",
   "the original entry is untouched — both remain")
r = core.correct_attempt(a1["id"], "srv_marta", outcome="whatever")
ok("refused" in r and "only the server" in r["refused"],
   "another server's version is a statement, not a correction")

print("== late-recorded is labeled forever ==")
late = core.record_attempt("sv_001", "srv_dre", "no answer", "9 Vance Blvd, Hardin County",
                           attempted_at=iso(now() - timedelta(days=3)))
ok(late["late_recorded"] is True, "recorded 72h after the attempt → late_recorded")
ok("permanent" in late["late_note"], "the label says it is permanent")
c2 = core.correct_attempt(late["id"], "srv_dre", outcome="no answer — dog in the yard")
ok(store.by_id("attempts", late["id"])["late_recorded"] is True,
   "correcting a late attempt never clears the original's label")
demo_late = core.attempts_for("sv_demo_late")
ok(demo_late and demo_late[0]["late_recorded"] is True, "seeded late-recorded fixture labeled")

print("== the affidavit assembles verbatim from the log, only ==")
r = agents.draft_affidavit("sv_demo_affidavit")
draft = r["draft"]
atts = core.attempts_for("sv_demo_affidavit")
ok(all(a["address"] in draft and a["outcome"] in draft for a in atts),
   "every attempt's address and outcome appear verbatim")
ok("AFFIDAVIT OF SERVICE" in draft, "a served serve drafts an affidavit of service")
ok("Software never signs and never attests" in draft, "the signature block names the rule")
ok(r["gate"]["rung"] == "R1", "the draft queues for a human — court paper never auto-files")
ok("yourco" not in draft.lower(), "white-label")
r = agents.draft_affidavit("sv_demo_affidavit", extra_fact="he also dodged me at his office")
ok("refused" in r and "no way into" in r["refused"], "an unlogged 'fact' is refused")
ok(any(e["kind"] == "refused"
       and (e["detail"] or {}).get("action") == "add_unrecorded_fact_to_affidavit"
       and (e["detail"] or {}).get("verbatim") == "he also dodged me at his office"
       for e in store.events()), "the request is preserved verbatim in the log")
r = agents.draft_affidavit("sv_demo_affidavit")
ok("dodged me at his office" not in r["draft"], "the planted fact never reaches a draft")
r = core.affidavit_draft("sv_demo_two")
ok("AFFIDAVIT OF DUE DILIGENCE" in r["draft"], "an unserved serve drafts due diligence, honestly")
r = agents.draft_affidavit("sv_h_nonexistent")
ok("error" in r, "no such serve → error")

print("== the late label rides into the draft ==")
r = agents.draft_affidavit("sv_demo_late")
ok("LATE-RECORDED" in r["draft"], "the affidavit discloses the late-recorded attempt")

print("== sign_or_attest: R0, never a slow yes ==")
r = agents.attest("sv_demo_affidavit")
ok(r.get("refused") and r["rung"] == "R0", "attest probe refused at R0")
ok("oath" in r["reason"], "the reason names the oath")
ok(not any(a["action"] == "sign_or_attest" and a["state"] == "pending"
           for a in store.load("approvals")), "NO approvable row — R0 is not a slow yes")

print("== due diligence: the recorded rule against the log itself ==")
r = agents.substitute("sv_demo_two")
ok("refused" in r, "substituted at 2 of 3 → refused")
ok("Hardin rule: 3 attempts across 2 hour-bands" in r["refused"], "the jurisdiction rule cited")
ok("2 attempt(s)" in r["refused"] and "1 more attempt" in r["refused"], "the gap is named")
ok(any(e["kind"] == "refused"
       and (e["detail"] or {}).get("action") == "declare_due_diligence_met"
       for e in store.events()), "declare_due_diligence_met refusal logged")
r = agents.substitute("sv_demo_diligent")
ok(r.get("allowed"), "the rule satisfied by the log → allowed")
ok("satisfied by the log itself" in r["basis"], "the basis is the log, not a story")
ok("a human signs" in r["note"], "even then, the oath stays human")
s_norule = {"id": "sv_x", "county": "Unrecorded"}
dd = core.due_diligence(s_norule, [])
ok(not dd["met"] and "no recorded due-diligence rule" in dd["why"],
   "a rule nobody recorded cannot authorize substituted service")

print("== the deadline board is the master clock ==")
db = core.deadline_board()
days = [r["days_to_deadline"] for r in db["rows"] if r["days_to_deadline"] is not None]
ok(days == sorted(days), "ranked by days-to-deadline, ascending")
ok(not any(r["serve"].startswith("sv_demo") for r in db["rows"]), "demo rows stay off the board")
unranked = [r for r in db["rows"] if r["days_to_deadline"] is None]
ok(all("_missing" in r for r in unranked) if unranked else True,
   "a serve with no deadline is named, never guessed")
ok("_source" not in db["rules_source"] and "replace with" in db["rules_source"],
   "the rules table names its source")

print("== the day list follows the court clock ==")
dl = core.day_list("srv_dre")
ddays = [r["days_to_deadline"] for r in dl["rows"] if r["days_to_deadline"] is not None]
ok(ddays == sorted(ddays), "a server's day is ordered by the court clock")
ok(all(r["assigned_to"] == "srv_dre" for r in dl["rows"]), "only their serves")

print("== the deadline-risk message ==")
out = agents.handle_message("ms_demo_deadline")
ok(out["classification"]["label"] == "deadline_risk", "the law firm's alarm is read as the alarm")
step = out["steps"][0]
ok(step["action"] == "flag_deadline_risk", "flagged to a human")
ok(any(e["kind"] == "flag_deadline_risk" and e["rung"] == "R2" for e in store.events()),
   "the flag executes at R2 — it cannot wait")
ok("2 attempt(s)" in step["draft"], "the reply counts the attempts from the record")
ok("Next attempt window" in step["draft"], "the reply names the next window")
ok("substituted service refused" in step["draft"], "the reply cites the rule gap honestly")
ok("yourco" not in step["draft"].lower(), "white-label")
ok(any(a["action"] == "draft_deadline_reply" and a["state"] == "pending"
       for a in store.load("approvals")), "the outward reply queues at R1 — a human sends")

print("== the status ask, answered from the record ==")
out = agents.handle_message("ms_demo_status")
step = out["steps"][0]
ok(step["action"] == "draft_status_reply", "answered, not escalated")
ok("3 attempt(s)" in step["draft"], "attempt count from the log")
ok("Next attempt window" in step["draft"], "next window from the uncovered bands")
ok("read straight from the attempt log" in step["draft"], "the reply names its basis")
ok("yourco" not in step["draft"].lower(), "white-label")

print("== assignment sweep ==")
sw = agents.assignment_sweep(limit=10_000)
ok(sw["proposed"] >= 1, "unassigned serves get proposed servers")
ok(any(a["action"] == "propose_assignment" and a["state"] == "pending"
       for a in store.load("approvals")), "proposals queue at R1")
sw2 = agents.assignment_sweep(limit=10_000)
ok(sw2["proposed"] == 0, "the sweep does not re-propose")

print("== matrix ==")
np = core.matrix.never_promote()
for a in ("sign_or_attest", "add_unrecorded_fact_to_affidavit", "declare_due_diligence_met"):
    ok(a in np, f"{a} never promotes")
ok(core.matrix.promotable("sign_or_attest", streak=1000)["promote"] is False,
   "a thousand clean runs still cannot buy the oath")
r = core.gate.act("add_unrecorded_fact_to_affidavit", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a["action"] == "add_unrecorded_fact_to_affidavit" and a["state"] == "pending"
           for a in store.load("approvals")), "R0 never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["n"] >= 15, "15+ labelled cases")
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no deadline-risk message missed")
ok("COLLAPSES" in ev["costly_note"], "the costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(r["recorded"]["serves_completed_90d"] > 0, "completions are counted, not asserted")
ok(r["recorded"]["rush_requests_90d"] > 0, "rush demand is counted")
labels = {l["label"]: l for l in r["lines"]}
q = labels["The quashed-service file"]
ok(q["kind"] == "scenario", "the quashed-service file is a scenario, never a saving")
ok(q["value"] is None and "quashed_value" in q["_missing"], "blank until the operator prices it")
ok(labels["Status-call hours returned"]["kind"] == "time_saved",
   "status hours never sum into revenue")
r2 = core.roi({"throughput_lift": 0.1, "serve_fee": 90})
ok(labels := {l["label"]: l for l in r2["lines"]}, "recompute")
ok(labels["Throughput on the day list"]["value"] is not None,
   "the throughput line computes once its inputs exist")

print("== recovered, counted (baseline delta) ==")
base = core.recovered_this_week()
sx = store.by_id("serves", "sv_000")
sx.update(status="served", completed_at=iso(now() - timedelta(hours=2)))
store.upsert("serves", sx)
rec = core.recovered_this_week()
ok(rec["serves_completed"] == base["serves_completed"] + 1, "a completion moves the count by 1")
ok(rec["fees_earned"] >= base["fees_earned"] + sx.get("fee", 0), "its fee lands in the counted total")
ok(rec["deadline_flags_raised"] >= 1, "the deadline flag was counted")
ok(rec["late_records_labeled"] >= 1, "late-record labels counted — caught, not hidden")
ok("counted" in rec["note"], "recovered names its basis")

print("== events append-only ==")
n_ev = len(store.events())
core.correct_attempt(a1["id"], "srv_dre", outcome="third version")
ok(len(store.events()) == n_ev + 1, "a correction ADDS an event; none are removed")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
