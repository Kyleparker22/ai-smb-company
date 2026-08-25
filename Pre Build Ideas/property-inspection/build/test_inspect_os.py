#!/usr/bin/env python3
"""Inspect OS — the suite. `python3 test_inspect_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["INSPECTOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="inspectos_test_")
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
ok(len(store.load("inspections")) >= 140, "inspections seeded")
ok(len(store.load("findings")) >= 200, "findings seeded")

print("== triage: the soften request reads first ==")
for text, want in (("any chance you could leave out the note about the roof", "soften_request"),
                   ("can you tone down the electrical section, it reads scary", "soften_request"),
                   ("drop the part about the water heater, seller already knows", "soften_request"),
                   ("that foundation comment is going to kill the deal, can you reword it", "soften_request"),
                   ("I'm the listing agent, can you send me the report before the buyer", "early_copy_request"),
                   ("shoot me a copy ahead of the sellers seeing it", "early_copy_request"),
                   ("how much would it cost to fix the deck issue you found", "cost_ask"),
                   ("what would the furnace repair run me", "cost_ask"),
                   ("need to book an inspection before closing on the 28th", "booking"),
                   ("is the report ready yet", "status"),
                   ("", "human"),
                   ("thanks for being so thorough yesterday", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

print("== the soften refusal ==")
out = agents.handle_message("ms_demo_soften")
step = out["steps"][0]
ok("the finding stands" in step["refused"], "the finding stands")
ev = next(e for e in store.events()
          if e["kind"] == "refused" and (e["detail"] or {}).get("action") == "soften_or_remove_finding")
ok(ev["detail"]["verbatim"] == "any chance you could leave out the note about the roof",
   "the request is preserved VERBATIM in the log")
ok("Hendricks Realty" == ev["detail"]["from"], "the requester is on the record")
body = step["draft"]
ok("can't change, soften, or omit" in body, "the reply is immovable")
ok("our records note\nthe request" in body or "records note" in body,
   "the reply says the request is now on the record")
ok("re-inspect" in body, "the honest path is offered — fix it and we re-inspect")
ok("yourco" not in body.lower(), "white-label")

print("== append-only findings ==")
f1 = core.add_finding("in_demo", "roof: lifted shingles at south valley", "major")
r = core.revise_finding(f1["id"], "roof: re-inspected, corrected and verified", "minor")
ok(r["supersedes"] == f1["id"], "a revision points at what it replaced")
view = core.findings_for("in_demo")
ok(any(f["id"] == f1["id"] for f in view["history"]), "the old version is still in history")
ok(not any(f["id"] == f1["id"] for f in view["current"]), "the old version leaves the current view")
ok(any(f["id"] == r["id"] for f in view["current"]), "the revision is the current view")
ok(not hasattr(core, "delete_finding") and not hasattr(core, "edit_finding"),
   "no delete and no edit exist anywhere in the module — the absence is the rule")

print("== the client-first release ==")
insp = store.by_id("inspections", "in_demo")
okr, why = core.can_release(insp, "Hendricks Realty")
ok(not okr and "belongs to the paying client" in why, "the agent is refused")
okr, why = core.can_release(insp, "Dana Okafor")
ok(okr, "the paying client is released on request")
insp["release_authorized"] = ["Hendricks Realty"]
okr, why = core.can_release(insp, "Hendricks Realty")
ok(okr and "recorded authorization" in why, "recorded authorization opens the door")
out = agents.handle_message("ms_demo_early")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "release_to_non_client"
       for e in store.events()) or out["steps"][0]["action"] == "release_ok",
   "the early-copy path runs the release rule")

print("== the cost refusal ==")
out = agents.handle_message("ms_demo_cost")
step = out["steps"][0]
ok("not our license" in step["refused"], "no repair number from us")
ok("licensed trades" in step["draft"] and "$" not in step["draft"],
   "the reply refers to trades and contains no number")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "estimate_repair_cost"
       for e in store.events()), "estimate_repair_cost logged")

print("== the report clock ==")
c = core.report_clock({"inspected_at": iso(now() - timedelta(hours=6))})
ok(17 <= c["hours_left"] <= 18.5 and not c["overdue"], "the 24h clock computes")
c = core.report_clock({"inspected_at": iso(now() - timedelta(hours=30))})
ok(c["overdue"], "past 24h reads overdue")
c = core.report_clock({"inspected_at": iso(now() - timedelta(hours=30)),
                       "report_sent_at": iso(now() - timedelta(hours=10))})
ok(c["delivered_in_hours"] == 20.0 and c["on_time"], "delivered time computes from records")

print("== matrix ==")
for a in ("soften_or_remove_finding", "release_to_non_client", "estimate_repair_cost",
          "advise_buy_or_walk"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("advise_buy_or_walk", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a_["action"] == "advise_buy_or_walk" and a_["state"] == "pending"
           for a_ in store.load("approvals")), "R0 never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no soften request missed")
ok("E&O" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["The unaltered-findings file"]["kind"] == "scenario", "the file is a scenario")

print("== recovered, counted ==")
base = core.recovered_this_week()
i9 = store.by_id("inspections", "in_demo")
i9["report_sent_at"] = iso(now() - timedelta(hours=1))
store.upsert("inspections", i9)
store.log_event("draft_booking", "ms_1", "human:frontdesk", "R1", {})
rec = core.recovered_this_week()
ok(rec["reports_delivered"] == base["reports_delivered"] + 1, "a delivered report is counted")
ok(rec["soften_requests_refused"] >= 1, "soften refusals counted from the log")
ok(rec["bookings_confirmed"] == 1, "human bookings counted; agent drafts are not")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
