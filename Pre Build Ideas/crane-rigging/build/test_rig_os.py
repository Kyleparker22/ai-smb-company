#!/usr/bin/env python3
"""Rig OS — the suite. `python3 test_rig_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["RIGOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="rigos_test_")
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
ok(len(store.load("lifts")) >= 30, "lifts seeded")

print("== critical flags ==")
for text, want in (("set trusses over the occupied school gym wing", True),
                   ("tandem pick with both cranes for the vessel", True),
                   ("need a man basket for the crew at the stack", True),
                   ("load's heavy for the 90-tonner, probably 85% of chart", True),
                   ("blind pick over the back of the building", True),
                   ("night lift over the water at the marina", True),
                   ("set two hvac units on a strip mall roof, sunday morning closed", False),
                   ("hang steel for a two-story frame, open site", False),
                   ("lift a hot tub over a one-story ranch house, nobody home", False),
                   ("set a generator beside the substation access road", False)):
    ok(core.rfq_flags(text)["critical"] == want, f"flags: {text[:44]} → critical={want}")

print("== the critical RFQ path ==")
out = agents.handle_rfq("rf_demo_critical")
ok(out["steps"][0]["action"] == "route_to_engineering", "critical routes to engineering only")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "quote_critical_as_taxi"
       for e in store.events()), "quote_critical_as_taxi logged")
body = out["steps"][0]["draft"]
ok("compliment to the job" in body and "lift director" in body,
   "the copy sells the engineering path")
ok("yourco" not in body.lower(), "white-label")

print("== site-data quoting ==")
out = agents.handle_rfq("rf_demo_nodata")
ok(out["steps"][0]["action"] == "estimate_pending_site_visit", "no data → site visit")
ok("radius_ft" in out["steps"][0]["refused"], "missing fields named")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "quote_firm_without_site_data"
       for e in store.events()), "quote_firm_without_site_data logged")
out = agents.handle_rfq("rf_demo_clean")
ok(out["steps"][0]["action"] == "draft_quote", "recorded site data → a quote drafts")
ok("9000lbs at 55ft" in out["steps"][0]["why"], "the quote cites the site data")

print("== the lift-plan rule ==")
r = agents.schedule_lift("lf_demo_noplan")
ok("refused" in r and "lift director signs" in r["refused"], "critical without a plan refused")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "approve_lift_plan"
       for e in store.events()), "approve_lift_plan logged")
r = agents.schedule_lift("lf_demo_planned")
ok(r.get("rung") == "R1" and r.get("approval"), "a planned critical lift schedules at R1")
oks, why = core.can_schedule_lift(store.by_id("lifts", "lf_demo_planned"))
ok("LP-441" in why and "nothing more" in why,
   "the check names the record and its own limited role")

print("== the cert gate ==")
r = agents.assign_operator("lf_demo_planned", "op_demo_tss")
ok("refused" in r and "TLL" in r["refused"], "a TSS card doesn't swing the AT")
ok("lattice boom" in r["refused"], "the stake named")
r = agents.assign_operator("lf_demo_planned", "op_demo_tll")
ok(r.get("rung") == "R1" and r.get("approval"), "a TLL cert assigns at R1")

print("== the wind gate ==")
r = agents.dispatch_today("lf_demo_windy", forecast_mph=30)
ok("refused" in r and "stands the job down" in r["refused"], "over the limit → stood down")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "dispatch_over_wind_limit"
       for e in store.events()), "dispatch_over_wind_limit logged")
r = agents.dispatch_today("lf_demo_windy", forecast_mph=12)
ok(r.get("dispatchable"), "inside the limit dispatches")
okd, why = core.can_dispatch_today({"wind_limit_mph": None}, 10)
ok(not okd and "a guess is not a limit" in why, "no recorded limit → no dispatch")
okd, why = core.can_dispatch_today({"wind_limit_mph": 20}, None)
ok(not okd and "waits for the number" in why, "no forecast → dispatch waits")

print("== cert sweep ==")
out = agents.cert_sweep()
ok(out["alerts"] >= 0, "sweep runs")

print("== matrix ==")
for a in ("approve_lift_plan", "assign_uncertified_operator", "dispatch_over_wind_limit",
          "quote_critical_as_taxi", "quote_firm_without_site_data"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("approve_lift_plan", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no critical lift missed")
ok("routine" in ev["costly_note"].lower(), "costly note names the stake")

print("== roi ==")
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["The lift-plan file"]["kind"] == "scenario",
   "a crane that didn't tip is never a saving")

print("== recovered, counted ==")
base = core.recovered_this_week()
l9 = store.by_id("lifts", "lf_demo_planned")
l9["completed_at"] = iso(now() - timedelta(days=1))
store.upsert("lifts", l9)
store.log_event("draft_quote", "rf_demo_clean", "human:estimator", "R1", {})
rec = core.recovered_this_week()
ok(rec["lifts_completed"] == base["lifts_completed"] + 1, "completed lifts counted")
ok(rec["quotes_sent"] == 1, "human quotes counted; agent drafts are not")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
