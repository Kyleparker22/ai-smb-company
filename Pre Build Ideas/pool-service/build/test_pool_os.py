#!/usr/bin/env python3
"""Pool OS — the suite. `python3 test_pool_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["POOLOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="poolos_test_")
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
ok(len(store.load("stops")) >= 900, "stops seeded")
ok(len(store.load("customers")) == 450, "customers seeded")

print("== triage: injury reads first ==")
for text, want in (("my son got a chemical burn on his legs after swimming yesterday", "injury"),
                   ("our guest slipped on the deck by the ladder and hit his head", "injury"),
                   ("the neighbor kid almost drowned, we pulled him out ourselves", "injury"),
                   ("the dog went under near the drain and got stuck for a second", "injury"),
                   ("how much shock should I add after the party", "chemical_question"),
                   ("can I dump bleach in until you get here", "chemical_question"),
                   ("pool turned green over the weekend", "green_pool"),
                   ("there are tadpoles in the pool somehow", "green_pool"),
                   ("skip this week's service, we're out of town", "schedule"),
                   ("gate code is 7741 starting monday", "schedule"),
                   ("", "human"),
                   ("invoice received, thanks for the great work", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:40]} → {want}")

print("== the injury protocol ==")
out = agents.handle_message("ms_demo_injury")
step = out["steps"][0]
ok(step["action"] == "log_injury_report", "injury logged verbatim")
ok("nothing is admitted, denied, or assessed" in step["said"].lower()
   or "admitted, denied, or assessed" in step["said"], "protocol: no admission, no denial")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "respond_to_injury_report"
       for e in store.events()), "respond_to_injury_report refused + logged")

print("== the chemical question goes unanswered ==")
out = agents.handle_message("ms_demo_dose")
ok(out["steps"][0].get("refused") == "routed unanswered", "dosing question refused")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "answer_chemical_dosing"
       for e in store.events()), "answer_chemical_dosing logged")

print("== the service-proof billing gate ==")
okb, why = core.can_bill_stop(store.by_id("stops", "st_demo_proven"))
ok(okb and "FC 2.4" in why, "complete proof bills, citing the readings")
okb, why = core.can_bill_stop(store.by_id("stops", "st_demo_noproof"))
ok(not okb, "missing proof refused")
ok("PH" in why and "TA" in why and "arrival stamp" in why, "refusal names each missing field")
ok("unprovable service" in why, "refusal names the stake")
r = agents.bill_stop("st_demo_noproof")
ok("refused" in r, "bill_stop refuses")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "bill_unproven_stop"
       for e in store.events()), "bill_unproven_stop logged")
r = agents.bill_stop("st_demo_proven")
ok(r.get("rung") == "R1" and r.get("approval"), "proven stop queues at R1")

print("== readings report, never a verdict ==")
pool = {"target_ranges": {"fc": [1.0, 4.0], "ph": [7.2, 7.8], "ta": [80, 120]}}
rep = core.reading_report(pool, {"readings": {"fc": 5.5, "ph": 7.5, "ta": None}})
rows = {r["param"]: r for r in rep["rows"]}
ok(rows["FC"]["in_range"] is False, "out-of-range flagged")
ok(rows["PH"]["in_range"] is True, "in-range flagged")
ok(rows["TA"].get("_missing"), "missing reading refuses, never zero-fills")
ok("safe" not in str(rep).lower() or "'safe to swim' never leaves" in rep["note"],
   "no swim verdict anywhere in the report")
rep2 = core.reading_report({"target_ranges": {}}, {"readings": {"fc": 2.0, "ph": 7.4, "ta": 90}})
ok(all("no target range" in (r.get("note") or "") for r in rep2["rows"]),
   "no recorded ranges → flagged, not judged")

print("== drafted copy ==")
body = agents._recovery_copy({"from": "Osei household"})
ok("2–4 visits" in body or "2-4 visits" in body, "recovery copy promises visits, not a date")
ok("your call on swimming" in body.lower() or "your call" in body,
   "the swim decision stays with the owner and the numbers")
ok("safe to swim" not in body.lower(), "the forbidden words never appear")
ok("yourco" not in body.lower(), "white-label: no yourco name in outward copy")
q9 = {"id": "qt_x", "customer_name": "Dana Mercer", "item": "salt cell replacement",
      "amount": 940, "sent_at": iso(now() - timedelta(days=10))}
b1 = agents._quote_chase_copy(q9, 1)
ok("Dana" in b1 and "$940" in b1 and "salt cell" in b1, "quote chase carries the finding and number")
b3 = agents._quote_chase_copy(q9, 3)
ok("last note" in b3.lower() and "leave it on your file" in b3, "touch 3 closes without pressure")
ok(not any(w in (b1 + b3).lower() for w in ("unsafe", "danger", "risk")),
   "no scare language in quote copy")

print("== the quote ladder ==")
store.upsert("quotes", q9)
plan = core.quote_plan(q9)
ok(plan["action"] == "draft_chase", "an aged quote is due a touch")
q9["touches"] = [{"at": iso(now() - timedelta(days=2))}]
ok(core.quote_plan(q9)["action"] == "none", "7-day cooldown holds")
q9["touches"] = [{"at": iso(now() - timedelta(days=30 - i))} for i in range(3)]
ok("silence is an answer" in core.quote_plan(q9)["why"], "ladder exhausts at 3")

print("== matrix ==")
for a in ("respond_to_injury_report", "declare_safe_to_swim", "answer_chemical_dosing",
          "bill_unproven_stop"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("declare_safe_to_swim", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a_["action"] == "declare_safe_to_swim" and a_["state"] == "pending"
           for a_ in store.load("approvals")), "R0 never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no injury report missed")
ok("LAWSUIT" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("unbilled_stops_value" in r["recorded"], "unbilled value recorded")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Equipment quotes recovered"]["value"] is None,
   "quote line blank without the operator's close rate")
ok(labels["The liability file"]["kind"] == "scenario", "liability is a scenario, never a saving")

print("== recovered, counted ==")
base = core.recovered_this_week()
s9 = store.by_id("stops", "st_demo_proven")
s9["billed_at"] = iso(now() - timedelta(days=1))
store.upsert("stops", s9)
q9["won_at"] = iso(now())
store.upsert("quotes", q9)
store.log_event("draft_recovery_visit", "ms_demo_green", "human:frontdesk", "R1", {})
rec = core.recovered_this_week()
ok(rec["stops_billed"] == base["stops_billed"] + 1, "a billed stop is counted")
ok(rec["quotes_won"] == base["quotes_won"] + 1 and rec["won_value"] >= 940,
   "a won quote is counted with its value")
ok(rec["recovery_visits_booked"] == 1, "human-booked recovery visits are counted")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a, "automation rate field present")
ok(a.get("rate") is not None or "_missing" in a, "below-floor refuses with a reason")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
