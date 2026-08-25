#!/usr/bin/env python3
"""Flue OS — the suite. `python3 test_flue_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["FLUEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="flueos_test_")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from datetime import datetime, timedelta, timezone

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


OCT = datetime(2026, 10, 15, tzinfo=timezone.utc)
AUG = datetime(2026, 8, 17, tzinfo=timezone.utc)

print("== seed ==")
seed.main()
ok(len(store.load("households")) >= 1900, "~1,900 households seeded")
ok(len(store.load("techs")) == 3, "3 techs")
ok(store.load("config").get("company") == "Hearthstone Chimney Co.", "operator named")
db = seed.core.due_board()
ok(db["due"] > 300, f"a real due slice ({db['due']} due for annual)")
ok(db["no_record"] > 0, "a no-record slice, counted separately")
ok(len(core.hazard_households()) > 0, "some households carry stage-3/hazard findings")

print("== triage: the CO/smoke event reads first ==")
for text, want in (
        ("the carbon monoxide alarm keeps going off when the furnace runs", "co_smoke_event"),
        ("smoke filling the living room when we light a fire", "co_smoke_event"),
        ("our co detector went off twice last night", "co_smoke_event"),
        ("smoke is pouring into the house from the fireplace", "co_smoke_event"),
        ("CARBON MONOXIDE ALARM WON'T STOP", "co_smoke_event"),
        ("the detectors keep tripping, is it co", "co_smoke_event"),
        ("we had a chimney fire last night, the fire department came", "chimney_fire_aftermath"),
        ("flames were shooting out of the chimney top yesterday", "chimney_fire_aftermath"),
        ("the flue was glowing and roaring during the fire", "chimney_fire_aftermath"),
        ("is it safe to use the fireplace this winter", "safe_to_burn_ask"),
        ("safe to burn after last year's sweep", "safe_to_burn_ask"),
        ("can we light a fire before the holidays", "safe_to_burn_ask"),
        ("is the wood stove okay to run", "safe_to_burn_ask"),
        ("need to schedule our annual sweep", "booking"),
        ("book a chimney cleaning before october please", "booking"),
        ("when can you fit a sweep in", "booking"),
        ("how much for a new chimney cap", "quote"),
        ("price to reline the flue", "quote"),
        ("estimate for the crown repair you flagged", "quote"),
        ("", "human"),
        ("do you sell firewood", "human"),
        ("thanks, the tech was great", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44] or '(empty)'} → {want}")
# the costly label wins even when a booking phrase rides along
ok(core.read_message("need to schedule a sweep but the carbon monoxide alarm keeps going off")
   ["label"] == "co_smoke_event", "CO beats booking in the same message")
ok(core.read_message("safe to burn? we had a chimney fire last week")["label"]
   == "chimney_fire_aftermath", "aftermath beats the burn ask in the same message")

print("== the evacuate script — verbatim, and never a booking ==")
out = agents.handle_message("ms_demo_co")
step = out["steps"][0]
ok(step["action"] == "escalate_co_event", "the CO event escalates")
ok(step["draft"] == core.EVACUATE_SCRIPT, "the evacuate script is the reply, VERBATIM")
ok("911" in step["draft"] and "never a booking" in step["draft"],
   "the script says 911 and refuses the booking in its own words")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "co_event_as_booking"
       for e in store.events()), "co_event_as_booking refused + logged")
ok(not any(a["action"] in ("draft_booking_reply", "draft_quote_reply")
           and a["subject"] == "ms_demo_co" for a in store.load("approvals")),
   "no booking draft was queued for the CO event")
ok(any(e["kind"] == "escalate_co_event" and e.get("rung") == "R2" for e in store.events()),
   "the escalation ran at R2 — it cannot wait for a click")
ok("yourco" not in step["draft"].lower(), "white-label: the script")

print("== safe to burn: the record cited ==")
out = agents.handle_message("ms_demo_burn")
step = out["steps"][0]
ok(step["action"] == "draft_burn_reply", "a recorded Level 2 → the citation drafts")
ok("Level 2" in step["draft"], "the level is cited")
ok("Dana Okafor" in step["draft"], "the tech is cited")
ok("light first-stage soot, brushed clean" in step["draft"], "the findings are cited verbatim")
ok("Nothing beyond that record is declared" in step["draft"],
   "the draft declares nothing beyond the record")
ok(any(a["action"] == "draft_burn_reply" and a["state"] == "pending"
       for a in store.load("approvals")), "the citation queues at R1 — a human sends")
ok("yourco" not in step["draft"].lower(), "white-label: the citation")

print("== safe to burn: no record → book the inspection, refused ==")
out = agents.handle_message("ms_demo_burn_none")
step = out["steps"][0]
ok(step["action"] == "book_the_inspection", "no record → book the inspection")
ok("Book the inspection" in step["draft"], "the draft says book the inspection")
ok("guess we won't put in writing" in step["draft"], "the draft explains the honesty")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "declare_safe_to_burn"
       for e in store.events()), "declare_safe_to_burn refused + logged")
ok(not any(a["action"] == "declare_safe_to_burn" for a in store.load("approvals")),
   "R0 never becomes an approvable row")
v = core.burn_verdict(store.by_id("households", "hh_demo_none"))
ok(v["verdict"] == "book_the_inspection" and "house fire with a chat log" in v["why"],
   "the verdict names the stake")

print("== stale record is also 'book the inspection' ==")
hh_l2 = store.by_id("households", "hh_demo_l2")
stale = dict(hh_l2)
stale["inspections"] = [dict(hh_l2["inspections"][0], date=iso(now() - timedelta(days=500)))]
v = core.burn_verdict(stale)
ok(v["verdict"] == "book_the_inspection" and "stale" in v["why"],
   "a 500-day-old record does not clear a burn verdict")

print("== the hazard survives verbatim — every draft ==")
STAGE3 = seed.STAGE3_TEXT
out = agents.handle_message("ms_demo_burn_stage3")
step = out["steps"][0]
ok(STAGE3 in step["draft"], "the stage-3 finding survives VERBATIM in the burn reply")
ok("we won't soften this" in step["draft"], "the reply says so")
ok("Do not light a fire" in step["draft"], "the reply forbids the fire until remediation")
ok(core.soften_ok(step["draft"])[0], "no softening language in the shipped reply")
r = agents.draft_report("hh_demo_stage3")
ok(STAGE3 in r["body"], "the stage-3 finding survives VERBATIM in the report draft")
ok("IMG_0231" in r["body"], "the recorded photo is referenced")
ok("HAZARD" in r["body"], "the hazard is flagged, not buried")
ok(r["gate"]["rung"] == "R1", "the report queues for a human — never auto-sends")
ok("yourco" not in r["body"].lower(), "white-label: the report")
# the structural checks themselves
findings = [{"text": STAGE3, "hazard": True}]
ok(not core.hazard_verbatim_ok("the flue could use a cleaning", findings)[0],
   "a rephrased hazard fails the verbatim check")
ok(core.hazard_verbatim_ok("verbatim: " + STAGE3, findings)[0],
   "the verbatim text passes")
ok(not core.soften_ok("stage 3, but it's probably fine — could use a cleaning")[0],
   "softener phrases are structurally refused")
r = agents.draft_report("hh_demo_none")
ok("refused" in r and "never from memory" in r["refused"],
   "no recorded inspection → the report refuses, never pads")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "draft_report"
       for e in store.events()), "the report refusal is logged")

print("== chimney-fire aftermath forces Level 3 per the recorded rule ==")
out = agents.handle_message("ms_demo_fire")
step = out["steps"][0]
ok(step["action"] == "book_level3", "the aftermath books the Level 3")
ok("Level 3" in step["draft"], "Level 3 is named in the draft")
ok("not a sweep" in step["draft"], "a sweep is explicitly not the response")
ok("NFPA 211" in step["draft"], "the recorded rule is cited by source")
ok("911" in step["draft"], "anything still burning is 911 first")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "sweep_after_chimney_fire"
       for e in store.events()), "sweep_after_chimney_fire refused + logged")

print("== the recall ladder: bounded, cooled, seasonal ==")
due_hh = next(h for h in store.load("households")
              if not h.get("demo_tag")
              and (core.service_age_days(h) or 0) >= 365)
plan = core.recall_plan(due_hh)
ok(plan["action"] == "draft_recall" and "touch 1 of 3" in plan["why"], "a due household drafts")
maxed = dict(due_hh, recall_touches=[{"at": iso(now() - timedelta(days=99))}] * 3)
ok(core.recall_plan(maxed)["action"] == "none", "ladder exhausted at 3 — silence is an answer")
cooling = dict(due_hh, recall_touches=[{"at": iso(now() - timedelta(days=3))}])
p = core.recall_plan(cooling)
ok(p["action"] == "none" and "cooldown" in p["why"], "inside the 21-day cooldown → no touch")
norec = {"id": "x", "name": "X"}
p = core.recall_plan(norec)
ok(p["action"] == "none" and "spam" in p["why"], "no recorded service → no recall (spam rule)")
ok(core.recall_plan(store.by_id("households", "hh_demo_stage3"))["action"] == "none",
   "demo fixtures are never recalled")
sb_oct = core.season_board(OCT)
ok(sb_oct["overflow"] > 0 and sb_oct["peak"], "October: the due book exceeds tech-day capacity")
ok(sb_oct["offer"] and sb_oct["offer"]["discount_pct"] == 15,
   "overflow is offered February at the RECORDED off-season rate")
body = agents._recall_copy(due_hh, 1, offer=sb_oct["offer"], sb=sb_oct)
ok("February" in body and "15%" in body, "the recall copy carries the February offer")
ok("recorded off-season rate" in body, "the copy names the rate as recorded")
sb_aug = core.season_board(AUG)
ok(sb_aug["offer"] is None, "off-peak: no February offer — the season logic is month-aware")
cfg = store.load("config"); saved = cfg.pop("off_season_discount"); store.save("config", cfg)
offer = core.february_offer()
ok(offer["discount_pct"] is None and "not invented" in offer["note"],
   "no recorded rate → the slot is offered, the discount is not invented")
cfg["off_season_discount"] = saved; store.save("config", cfg)
swept = agents.recall_sweep(limit=5, ref=OCT)
ok(swept["drafted"] == 5, "the recall sweep drafts, capped at the limit")
ok(all(a["rung"] == "R1" for a in store.load("approvals")
       if a["action"] == "draft_recall"), "every recall queues at R1 — a human sends")
touched = [h for h in store.load("households") if h.get("recall_touches")]
ok(all(not h.get("demo_tag") for h in touched), "the sweep never touched a demo fixture")
ok(all("yourco" not in t.get("body", "").lower()
       for h in touched for t in h["recall_touches"]), "white-label: the recall copy")

print("== matrix ==")
for a in ("declare_safe_to_burn", "soften_hazard_finding", "co_event_as_booking",
          "sweep_after_chimney_fire"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("soften_hazard_finding", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a["action"] in core.matrix.never_promote() and a["state"] == "pending"
           for a in store.load("approvals")), "no R0 action ever has an approvable row")
ok(core.matrix.promotable("declare_safe_to_burn", 1000)["promote"] is False,
   "a thousand-clean streak still cannot promote the burn verdict")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no CO/smoke event missed")
ok("CARBON MONOXIDE" in ev["costly_note"] and "KILLS" in ev["costly_note"],
   "costly note names the CO stake in caps")
ok(ev["n"] >= 15, "a real labelled set")

print("== roi ==")
r = core.roi({})
ok(r["recorded"]["due_book"] == core.due_board()["due"], "the due book is counted, not typed")
ok(r["recorded"]["avg_ticket"] == 289, "the ticket comes from the recorded config")
ok("october_overflow" in r["recorded"], "the overflow is counted against capacity")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["The due book, re-called"]["value"] is None
   and "booking_rate" in labels["The due book, re-called"]["_missing"],
   "the recall line stays blank until the operator supplies the booking rate")
ok(labels["The house-fire file"]["kind"] == "scenario"
   and labels["The house-fire file"]["value"] is None,
   "the house-fire file is a scenario and renders blank — never a saving")
ok(labels["Office hours"]["kind"] == "time_saved", "office hours are time_saved, never revenue")
r2 = core.roi({"booking_rate": 0.3})
ok(r2["lines"][0]["value"] == round(r2["recorded"]["due_book"] * 289 * 0.3, 2),
   "the recall line shows its arithmetic when fed")

print("== recovered, counted ==")
base = core.recovered_this_week()
hh0 = next(h for h in store.load("households") if not h.get("demo_tag"))
hh0["last_sweep"] = iso(now() - timedelta(days=1))
store.upsert("households", hh0)
store.log_event("draft_recall", hh0["id"], "human:office", "R1", {})
rec = core.recovered_this_week()
ok(rec["households_swept"] == base["households_swept"] + 1, "a swept household is counted")
ok(rec["sweep_revenue"] == round(rec["households_swept"] * 289, 2),
   "sweep revenue = counted sweeps × the recorded ticket")
ok(rec["recalls_sent"] == base["recalls_sent"] + 1,
   "human-sent recalls counted; agent drafts are not")
ok(rec["co_events_escalated"] >= 1, "the CO escalation is counted")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a),
   "automation counted or refused — never asserted")

print("== append-only ==")
n0 = len(store.events())
ev1 = store.log_event("test_probe", "x", "human:test", None, {})
store.log_event("corrected", "x", "human:test", None, {"action": "test_probe"})
evs = store.events()
ok(len(evs) == n0 + 2, "a correction is a NEW event — nothing rewritten")
ok(any(e["id"] == ev1["id"] and e["kind"] == "test_probe" for e in evs),
   "the original event survives the correction")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
