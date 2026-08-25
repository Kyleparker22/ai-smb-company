#!/usr/bin/env python3
"""Reserve OS — the suite. `python3 test_reserve_os.py`."""
import inspect, os, sys, tempfile
from pathlib import Path

os.environ["RESERVEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="reserveos_test_")
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


INF = 9999


def hz_year(band):
    return band["horizon"]["year"] or INF


print("== seed ==")
seed.main()
assocs = store.load("associations")
ok(len(assocs) == 14, "14 associations seeded")
ok(len([v for v in store.load("violations") if not v.get("demo_tag")]) >= 120,
   "~120 violations seeded")
no_study = next(a for a in assocs if a["name"] == "Cedar Hollow")
stale_a = next(a for a in assocs if a["name"] == "Foxglove Green")
ok(no_study.get("reserve_study") is None, "one association has NO study")
ok(stale_a.get("reserve_study") is not None, "the stale association has a study")

print("== triage: safety reads first ==")
for text, want in (("the stairwell railing is loose", "safety"),
                   ("the pool gate latch is broken and kids are getting in", "safety"),
                   ("there's exposed wiring by the mailboxes in building C", "safety"),
                   ("a big tree limb came down across the walkway last night", "safety"),
                   ("the balcony railing on building B is coming loose", "safety"),
                   ("why did my dues go up this year", "dues_dispute"),
                   ("our assessment jumped forty dollars and nobody explained it", "dues_dispute"),
                   ("i was charged a late fee i don't owe", "dues_dispute"),
                   ("i want to appeal the violation notice about my flag", "appeal"),
                   ("i'm contesting the fine for the trash cans", "appeal"),
                   ("can i get a hearing about this notice", "appeal"),
                   ("how do i reserve the clubhouse for a birthday party", "amenity"),
                   ("my pool fob stopped working", "amenity"),
                   ("", "human"),
                   ("when is the next board meeting", "human"),
                   ("where do i find the approved paint colors", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44] or '(empty)'} → {want}")

print("== the safety protocol: routed NOW, verbatim ==")
out = agents.handle_message("ms_demo_safety")
step = out["steps"][0]
ok(step["action"] == "escalate_safety_report", "the safety report escalates")
ok(step["gate"]["executed"] is True and step["gate"]["rung"] == "R2",
   "escalation EXECUTES at R2 — never queued")
ok(step["verbatim"] == "the stairwell railing is loose", "the report travels verbatim")
esc_ev = [e for e in store.events(kind="escalate_safety_report")]
ok(esc_ev and esc_ev[-1]["detail"].get("verbatim") == "the stairwell railing is loose",
   "the event log carries the exact words")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "dismiss_safety_report"
       for e in store.events()), "dismiss_safety_report refused + logged")
ok("routed to the community" in step["draft"] and "ahead of everything else" in step["draft"],
   "the ack says what already happened")
ok("yourco" not in step["draft"].lower(), "white-label")

print("== funding bands: bear/base/bull against the recorded study ==")
briar = store.by_id("associations", "as_001")
fb = core.funding_bands(briar)
ok(set(fb["bands"]) == {"bear", "base", "bull"}, "three bands, always")
ok("THIS IS A MODEL" in fb["label"], "the bands label themselves a model")
ok("horizon is a band, never a date" in fb["label"], "the label names the horizon rule")
ok("DEFAULT construction-cost inflation" in fb["inflation_source"],
   "the inflation offsets are recorded and _source-named")
bear, base, bull = fb["bands"]["bear"], fb["bands"]["base"], fb["bands"]["bull"]
ok(bear["inflation"] > base["inflation"] > bull["inflation"],
   "bear runs hotter than base than bull")
ok(bear["end_balance"] < base["end_balance"] < bull["end_balance"],
   f"band math ordered: bear {bear['end_balance']} < base {base['end_balance']} "
   f"< bull {bull['end_balance']}")
ok(all("horizon" in b for b in fb["bands"].values()), "the horizon is per band")
ok(hz_year(bear) <= hz_year(base) <= hz_year(bull),
   "horizons ordered: bear no later than base no later than bull")
ok(hz_year(bear) != INF, "the demo association's bear horizon lands inside the window")
ok(any("negative" in b["horizon"]["note"] for b in fb["bands"].values()
       if b["horizon"]["year"]), "an in-window horizon names its basis")
ok(fb["stale"] is False, "a fresh study does not flag")

print("== the beyond-the-window honesty ==")
lark = core.funding_bands(store.by_id("associations", "as_002"))
ok(hz_year(lark["bands"]["base"]) == INF, "a well-funded association has no in-window horizon")
ok("beyond the" in lark["bands"]["base"]["horizon"]["note"]
   and "not a guarantee" in lark["bands"]["base"]["horizon"]["note"],
   "'beyond the study window' is stated honestly, never as a guarantee")

print("== UNKNOWABLE: no study, no adequacy claim ==")
r = core.adequacy(no_study["id"])
ok(r.get("unknowable") is True, "no study → UNKNOWABLE")
ok("no study, no adequacy claim" in r["refused"], "the refusal says the rule verbatim")
ok(any(e["kind"] == "refused"
       and (e["detail"] or {}).get("action") == "claim_adequacy_without_study"
       for e in store.events()), "claim_adequacy_without_study refused + logged")
bv_ns = core.board_view(no_study["id"])
ok(bv_ns["funding"].get("unknowable") is True, "the board door shows UNKNOWABLE, not a number")

print("== staleness: an old study flags every number ==")
fs = core.funding_bands(stale_a)
ok(fs["stale"] is True, "the 4.5-year-old study is stale against the 3-year threshold")
ok("EVERY number here is flagged" in fs["stale_note"], "the stale note flags everything")
ok(all(b.get("stale_flag") for b in fs["bands"].values()),
   "every band carries the stale flag")

print("== violations: no recorded rule, no violation — structurally ==")
before = len(store.load("violations"))
r = core.create_violation("as_001", "9A", "§99.9", "made-up complaint")
ok("refused" in r and "no rule, no violation" in r["refused"],
   "an unrecorded rule is refused with the rule named")
ok(len(store.load("violations")) == before, "no row was written — no code path exists")
ok(any(e["kind"] == "refused"
       and (e["detail"] or {}).get("action") == "violation_without_recorded_rule"
       for e in store.events()), "violation_without_recorded_rule logged")
r = core.create_violation("as_001", "9A", "§4.2", "trash containers at the curb since monday")
ok("violation" in r and r["violation"]["rule_title"].startswith("Trash containers"),
   "a recorded rule creates, with the rule carried verbatim")
ok(all(core.rule_for(store.by_id("associations", v["association_id"]), v["rule_section"])
       for v in store.load("violations")),
   "EVERY violation in the ledger resolves to a recorded rule — no exceptions seeded")

print("== the ladder: courtesy → notice → hearing, notices at R1 ==")
adv = agents.draft_violation_notice("vi_demo_courtesy")
ok(adv["advanced_to"] == "notice", "courtesy advances to notice")
ok(adv["gate"]["rung"] == "R1" and not adv["gate"]["executed"],
   "the outward notice queues R1 — a human sends")
ok("§4.2" in adv["draft"] and "Trash containers" in adv["draft"],
   "the notice cites the rule verbatim")
ok("courtesy → notice → hearing → fine" in adv["draft"], "the notice names the ladder")
v = store.by_id("violations", "vi_demo_hearing")
ok(agents.draft_violation_notice("vi_demo_hearing").get("refused"),
   "the ladder stops at the hearing — no advance past it")

print("== the hearing is a human act ==")
r = core.hearing_decide("vi_demo_hearing")
ok("refused" in r and "human act" in r["refused"], "no human, no decision")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "decide_hearing"
       for e in store.events()), "decide_hearing refused + logged")
r = core.hearing_decide("vi_demo_hearing", human="board_chair", outcome="upheld")
ok(r.get("decided") and r["stage"] == "fine", "a human decides; the stage moves")
ok(r["fine_amount"] == 100, "the fine is the recorded schedule's arithmetic (offense 1 → $100)")
ok("recorded schedule's arithmetic" in r["fine_basis"], "the basis names the schedule")

print("== the fine clamp ==")
r = agents.assess_fine("vi_demo_hearing", 250)
ok("refused" in r and "off-schedule" in r["refused"], "an off-schedule fine is refused")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "fine_off_schedule"
       for e in store.events()), "fine_off_schedule logged")
r = agents.assess_fine("vi_demo_hearing", 100)
ok(r.get("ok") and r["gate"]["rung"] == "R1", "the scheduled amount still waits for a human")
# a hearing-stage violation with a matching amount still refuses — the human first
hv = next(v for v in store.load("violations")
          if v.get("stage") == "hearing" and not v.get("demo_tag"))
sched = core.scheduled_fine(store.by_id("associations", hv["association_id"]),
                            hv.get("offense_n", 1))
r = core.check_fine(hv["id"], sched["amount"])
ok("refused" in r and "human act" in r["refused"],
   "even on-schedule, no fine lands before the human hearing decision")

print("== ONE LEDGER, TWO DOORS: the identity test ==")
bv = core.board_view("as_001")
hv = core.homeowner_view("as_001", "ho_demo")
ok(bv["funding"] == hv["funding"], "the funding numbers are IDENTICAL through both doors")
ok(bv["violations"]["total"] == hv["violations"]["total"],
   "the violation total is identical")
ok(bv["violations"]["by_stage"] == hv["violations"]["by_stage"],
   "the per-stage counts are identical")
ok(bv["dues"] == hv["dues"], "the dues line items are identical")
ok(all(r["unit"] == "14B" for r in hv["violations"]["rows"]),
   "the homeowner sees only her own unit's rows")
ok(len(hv["violations"]["rows"]) >= 1, "her own violation is visible, not hidden")
ok(hv["violations"]["others_redacted"]
   == len(bv["violations"]["rows"]) - len(hv["violations"]["rows"]),
   "redaction is counted, never silent")
ok("board_view(" in inspect.getsource(core.homeowner_view),
   "STRUCTURAL: the homeowner door calls board_view — one read path in the source")
ok("funding_bands(" not in inspect.getsource(core.homeowner_view),
   "the homeowner door never recomputes a number")

print("== the dues dispute, answered by citation ==")
out = agents.handle_message("ms_demo_dues")
step = out["steps"][0]
ok(step["action"] == "draft_dues_reply", "the dispute drafts a reply")
body = step["draft"]
for item in briar["dues_line_items"]:
    ok(item["label"] in body, f"line item cited verbatim: {item['label']}")
ok("bands, never one date" in body, "the horizon is given as bands, never one date")
ok("same books the board sees" in body, "the reply names the one-ledger rule")
ok("yourco" not in body.lower(), "white-label")
pend = [a for a in store.load("approvals")
        if a["action"] == "draft_dues_reply" and a["state"] == "pending"]
ok(pend and pend[-1]["rung"] == "R1", "the outward reply queues R1")

print("== the appeal: a recorded right ==")
out = agents.handle_message("ms_demo_appeal")
step = out["steps"][0]
ok(step["action"] == "draft_appeal_ack", "the appeal is acknowledged")
ok("courtesy → notice → hearing → fine" in step["draft"], "the hearing process is cited")
ok("made by a person" in step["draft"], "the ack says the decision is human")

print("== the board packet drafts R1 ==")
r = agents.draft_board_packet("as_001")
ok(r["gate"]["rung"] == "R1" and not r["gate"]["executed"],
   "the packet queues R1 — never auto-sent")
ok("horizon" in r["packet"] and "Violations:" in r["packet"],
   "the packet carries bands + ledger summary")
r = agents.draft_board_packet(no_study["id"])
ok("UNKNOWABLE" in r["packet"], "the no-study packet says UNKNOWABLE, not a number")

print("== matrix: the R0s ==")
for a in ("claim_adequacy_without_study", "violation_without_recorded_rule",
          "fine_off_schedule", "dismiss_safety_report", "decide_hearing"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
for a in ("dismiss_safety_report", "fine_off_schedule", "claim_adequacy_without_study"):
    r = core.gate.act(a, "probe", "x", {})
    ok(r.get("refused"), f"R0 probe {a} refused")
ok(not any(ap["action"] in core.matrix.never_promote() and ap["state"] == "pending"
           for ap in store.load("approvals")), "no R0 ever becomes an approvable row")
ok(core.matrix.actions["draft_violation_notice"]["rung"] == "R1", "outward notice is R1")
ok(core.matrix.actions["record_violation"]["rung"] == "R2", "internal ledger write is R2")
ok(core.matrix.actions["escalate_safety_report"]["rung"] == "R2",
   "safety escalation acts now and tells a human")

print("== eval ==")
ev = core.run_eval()
ok(ev["n"] >= 15, f"{ev['n']} labelled cases")
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no safety report missed")
ok("LAWSUIT" in ev["costly_note"], "the costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok("disputes_month" in r["recorded"], "disputes answered is counted, not asked for")
labels = {l["label"]: l for l in r["lines"]}
ok(labels["Violation-dispute hours returned"]["kind"] == "time_saved",
   "dispute hours are time_saved, never revenue")
sc = labels["Contracts won or kept on provable fairness"]
ok(sc["kind"] == "scenario" and sc["value"] is None and "_missing" in sc,
   "the scenario line renders blank until the operator states its value")
ok(labels["The special assessment that landed as a plan, not a shock"]["kind"] == "scenario",
   "the avoided shock is a scenario, never a claimed saving")

print("== the counted week: baseline → delta ==")
base_w = core.counted_this_week()
store.log_event("draft_violation_notice", "vi_demo_courtesy", "human:manager", "R1", {})
store.log_event("draft_dues_reply", "ms_demo_dues", "human:manager", "R1", {})
w = core.counted_this_week()
ok(w["notices_sent"] == base_w["notices_sent"] + 1, "a human-sent notice counts")
ok(w["disputes_answered"] == base_w["disputes_answered"] + 1, "a human-sent answer counts")
ok(w["safety_reports_escalated"] >= 1, "the safety escalation was counted")
ok("counted from the event log" in w["note"], "the week names its basis")

print("== demo_tag skipped ==")
ok(all(not v.get("demo_tag") for v in core.board_view("as_001")["violations"]["rows"]),
   "demo fixtures never appear in the board's counts")

print("== append-only ==")
n1 = len(store.events())
core.gate.act("dismiss_safety_report", "probe", "y", {})
n2 = len(store.events())
ok(n2 == n1 + 1, "a refusal is a NEW event — the log only grows")
ok(not hasattr(store, "delete_event"), "there is no delete path on the log")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a),
   "automation counted or refused — never asserted")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
