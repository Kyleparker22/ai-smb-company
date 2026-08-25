#!/usr/bin/env python3
"""Well OS — the suite. `python3 test_well_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["WELLOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="wellos_test_")
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
ok(len(store.load("systems")) >= 300, "systems seeded")
ok(len(store.load("wells")) >= 40, "wells seeded")
ok(len(store.load("lab_reports")) >= 10, "lab reports seeded")

print("== triage: the contamination worry reads first ==")
for text, want in (("my water smells like rotten eggs", "contamination"),
                   ("the water tastes metallic and my kid got sick", "contamination"),
                   ("brown water since yesterday", "contamination"),
                   ("is our water safe to drink", "contamination"),
                   ("there's sand and grit coming out of the tap water", "contamination"),
                   ("we have no water at the house this morning", "no_water"),
                   ("the pump won't start and the faucets are sputtering", "no_water"),
                   ("is my uv lamp due for a change", "service_due"),
                   ("time to swap the sediment filter?", "service_due"),
                   ("how much to drill a new well on our property", "quote"),
                   ("can you price a softener install", "quote"),
                   ("any update on our drilling permit", "status"),
                   ("when is the rig coming out", "status"),
                   ("", "human"),
                   ("what time do you open saturday", "human"),
                   ("do you sell bags of softener salt at the shop", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")
ok(core.read_message("brown water since yesterday and the pump quit")["label"] == "contamination",
   "costly first: contamination outranks no_water in a mixed message")

print("== the contamination protocol ==")
out = agents.handle_message("ms_demo_contam")
step = out["steps"][0]
ok(step["action"] == "log_contamination", "the worry is logged")
ok("recorded word-for-word" in step["draft"], "the ack names the verbatim record")
ok("lab" in step["draft"].lower() and "report" in step["draft"].lower(),
   "the ack routes potability to the lab")
ok(core.soothe_ok(step["draft"])[0], "the shipped copy passes its own soothe check")
ok(not core.soothe_ok("it's probably fine, nothing to worry about")[0],
   "soothing language is structurally refused")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "downgrade_contamination_worry"
       for e in store.events()), "downgrade_contamination_worry refused + logged")
ok(any(e["kind"] == "log_contamination"
       and (e["detail"] or {}).get("verbatim") == "my water smells like rotten eggs"
       for e in store.events()), "the message is recorded verbatim in the event")
ok("yourco" not in step["draft"].lower(), "white-label")

print("== the dry house is a P1 ==")
out = agents.handle_message("ms_demo_dry")
step = out["steps"][0]
ok(step["action"] == "log_no_water", "the dry house is logged")
ok("today" in step["draft"], "the draft owns the same-day stake")
ok("yourco" not in step["draft"].lower(), "white-label")

print("== the lab rule ==")
r = agents.answer_water_safe("we_demo_logged")
ok("answer" in r and "LR-26-0417" in r["answer"], "the answer cites the report id")
ok("Total coliform: ABSENT" in r["answer"], "the result is quoted verbatim")
ok("does not add to it" in r["answer"], "the system quotes the lab; it never adds a verdict")
r = agents.answer_water_safe("we_demo_nolog")
ok("refused" in r and "the lab does" in r["refused"], "no report → 'we don't know yet, the lab does'")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "declare_water_safe"
       for e in store.events()), "declare_water_safe refused + logged")

print("== the clock rule: overdue is never 'protected' ==")
s9 = store.by_id("systems", "sy_demo_overdue")
st = core.protection_status(s9)
ok(st["rows"][0]["protected"] is False and "past the recorded clock" in st["rows"][0]["why"],
   "an overdue lamp reads unprotected")
r = agents.claim_protected("sy_demo_overdue")
ok("refused" in r and "stops sterilizing" in r["refused"], "the protection claim is refused")
ok("never 'still fine'" in r["refused"], "an overdue lamp is never 'still fine'")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "claim_protection_past_clock"
       for e in store.events()), "claim_protection_past_clock logged")
noclock = {"id": "sy_test_unmeasured", "components": [{"kind": "uv_lamp", "interval_days": 365}]}
st = core.protection_status(noclock)
ok(st["rows"][0]["protected"] is None and "_missing" in st["rows"][0],
   "a clock nobody recorded is unmeasured, never assumed current")
ok(not core.can_claim_protected(noclock)[0], "unmeasured clocks cannot claim protection either")

print("== the quote gate ==")
r = agents.draft_quote("we_demo_nolog")
ok("refused" in r and "we measure, then we price" in r["refused"].lower(),
   "no log → refused, measure first")
ok("guess in writing" in r["refused"], "the refusal names the dishonesty")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "quote_without_well_log"
       for e in store.events()), "quote_without_well_log logged")
r = agents.draft_quote("we_demo_logged")
ok("depth 340 ft" in r["basis"] and "yield 12.0 gpm" in r["basis"], "the quote cites the recorded log")
ok(r["gate"]["rung"] == "R1", "the quote queues for a human — money never sends itself")

print("== the permit clocks are date alerts ==")
jb = core.job_board()
ok("DEFAULT" in jb["rules_source"] and "replace" in jb["rules_source"],
   "the rules table names itself a default to replace")
row = next((x for x in jb["rows"] if x.get("clock")), None)
ok(row is not None, "at least one job carries a clock")
ok(row and "DATE ALERT" in row["clock"]["label"], "county clocks are DATE ALERTS, not legal advice")
ok(row and isinstance(row["clock"]["days_left"], int), "the alert is a counted number of days")

print("== the reminder ladder ==")
plan = core.service_plan(s9)
ok(plan["action"] == "draft_reminder" and "touch 1 of 3" in plan["why"],
   "an overdue system is due a reminder")
s9b = dict(s9, reminder_touches=[{"at": iso(now() - timedelta(days=2))}])
ok(core.service_plan(s9b)["action"] == "none"
   and "cooldown" in core.service_plan(s9b)["why"], "a recent touch → cooldown")
s9c = dict(s9, reminder_touches=[{"at": iso(now() - timedelta(days=d))} for d in (60, 40, 20)])
plan = core.service_plan(s9c)
ok(plan["action"] == "none" and "silence is an answer" in plan["why"],
   "three touches → the ladder exits; silence is an answer")
b3 = agents._reminder_copy(s9, "uv_lamp", 3)
ok("won't keep asking" in b3, "touch 3 says it stops")
ok("yourco" not in b3.lower(), "white-label")

print("== the sweep is capped and skips demo fixtures ==")
out = agents.service_sweep()
ok(out["drafted"] >= 1, "overdue systems get drafted reminders")
ok(out["drafted"] <= 20, "the sweep is capped")
ok(not (store.by_id("systems", "sy_demo_overdue").get("reminder_touches")),
   "the demo fixture is skipped by the sweep")

print("== the due board ==")
db = core.due_board()
ok(db["overdue_count"] >= 1 and db["due_value"] > 0, "the due book is counted")
ok(db["unknown_clocks"] >= 1, "unrecorded clocks are counted as unmeasured, not current")
ok("unmeasured" in db["note"], "the board names the honesty rule")

print("== matrix ==")
for a in ("declare_water_safe", "downgrade_contamination_worry",
          "claim_protection_past_clock", "quote_without_well_log"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("declare_water_safe", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a_["action"] == "declare_water_safe" and a_["state"] == "pending"
           for a_ in store.load("approvals")), "R0 never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no contamination worry missed")
ok("SAY-SO" in ev["costly_note"], "costly note names the health stake, in caps")

print("== roi ==")
r = core.roi({})
ok("due_service_value" in r["recorded"] and "overdue_service_value" in r["recorded"],
   "the service book is counted into the panel")
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
labels = {l["label"]: l for l in r["lines"]}
ok(labels["Missed-service revenue on the books"]["kind"] == "revenue"
   and labels["Missed-service revenue on the books"]["value"] is not None,
   "the counted line computes")
fines = labels["Permit fines avoided"]
ok(fines["kind"] == "scenario" and fines["value"] is None and "_missing" in fines,
   "the fines scenario stays blank — never our estimate")
ok(labels["Office hours"]["kind"] == "time_saved", "office hours are time_saved, never revenue")

print("== recovered, counted ==")
base = core.recovered_this_week()
store.log_event("draft_service_reminder", "sy_000", "agent:service", "R1", {})
mid = core.recovered_this_week()
ok(mid["reminders_sent"] == base["reminders_sent"], "an agent draft does not count as sent")
store.log_event("draft_service_reminder", "sy_000", "human:office", "R1", {})
rec = core.recovered_this_week()
ok(rec["reminders_sent"] == base["reminders_sent"] + 1, "a human send counts")
s0 = store.load("systems")[0]
s0["components"][0]["last_service_at"] = iso(now() - timedelta(days=1))
store.upsert("systems", s0)
rec2 = core.recovered_this_week()
ok(rec2["services_completed"] == rec["services_completed"] + 1, "a completed service counts")
ok("counted" in rec2["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print("== the log is append-only ==")
n = len(store.events())
first = dict(store.events()[0])
store.log_event("probe", "x", "human:test", None, {})
evs = store.events()
ok(len(evs) == n + 1, "events only append")
ok(evs[0] == first, "old events are never rewritten")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
