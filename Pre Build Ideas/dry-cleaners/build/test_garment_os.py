#!/usr/bin/env python3
"""Garment OS — the suite. `python3 test_garment_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["GARMENTOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="garmentos_test_")
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
ok(len(store.load("orders")) >= 400, "orders seeded")

print("== triage: the claim reads first ==")
for text, want in (("my wedding dress came back with a mark on the train", "claim"),
                   ("you shrunk my husband's suit two sizes", "claim"),
                   ("there's a hole in the silk blouse that wasn't there", "claim"),
                   ("the gown came back discolored at the hem", "claim"),
                   ("can you get red wine out of a linen shirt", "stain_ask"),
                   ("will the ink stain come out of this dress", "stain_ask"),
                   ("grease stain on my favorite jacket, any hope", "stain_ask"),
                   ("is my order ready for pickup", "pickup"),
                   ("are my shirts done for friday", "pickup"),
                   ("the hotel needs the napkin count corrected on the invoice", "wholesale"),
                   ("restaurant linen delivery moved to tuesday", "wholesale"),
                   ("", "human"),
                   ("what time do you close saturday", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

print("== the claim protocol ==")
out = agents.handle_message("ms_demo_claim")
step = out["steps"][0]
ok(step["action"] == "log_claim", "the claim is logged")
ok("published fair-claims schedule" in step["draft"] and "not haggled" in step["draft"],
   "the ack names the procedure")
ok("Nothing about your claim is decided by this message" in step["draft"],
   "nothing decided by software")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "deny_claim"
       for e in store.events()), "deny_claim refused + logged")
ok("yourco" not in step["draft"].lower(), "white-label")

print("== the schedule math ==")
r = agents.draft_settlement("cl_demo_full")
ok(r["math"]["amount"] == 2400 * 0.7, "the settlement is the schedule's arithmetic")
ok("the recorded\nschedule's arithmetic" in r["math"]["basis"]
   or "schedule's arithmetic" in r["math"]["basis"], "the basis names the schedule")
ok(r["gate"]["rung"] == "R1", "the draft queues for a human — never auto-settles")
ok(r["evidence"]["has_intake"] and "beading loose" in r["evidence"]["notes"],
   "the intake tag notes ride along")
r = agents.draft_settlement("cl_demo_partial")
ok("refused" in r and "age_years" in r["refused"] and "replacement_value" in r["refused"],
   "missing inputs → refused with fields named")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "settle_off_schedule"
       for e in store.events()), "settle_off_schedule logged")

print("== the promise rule ==")
out = agents.handle_message("ms_demo_stain")
body = out["steps"][0]["draft"]
ok("We'll\ntry" in body or "We'll try" in body.replace("\n", " "), "'we'll try' is the promise")
ok(core.promise_ok(body)[0], "the shipped copy passes its own check structurally")
ok(not core.promise_ok("that will come out no problem, guaranteed")[0],
   "promise language is structurally refused")
ok("anyone who promises more than that over text is guessing" in body.replace("\n", " ")
   or "guessing" in body, "the copy explains the honesty")

print("== the rack ladder + disposal clock ==")
o9 = store.by_id("orders", "or_demo_aging")
plan = core.rack_plan(o9)
ok(plan["action"] == "draft_reminder", "an aging order is due a reminder")
b3 = agents._rack_copy(o9, 3)
ok("hold them past it, no charge" in b3, "touch 3 offers to hold past the clock, free")
r = agents.dispose("or_demo_aging")
ok("refused" in r and "conversion, not cleanup" in r["refused"],
   "disposal before the clock refused")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "dispose_before_clock"
       for e in store.events()), "dispose_before_clock logged")
r = agents.dispose("or_demo_expired")
ok("refused" in r and "a human act" in r["refused"],
   "even past the clock, no human → no disposal")
r = agents.dispose("or_demo_expired", human="owner")
ok(r.get("disposed") and "only now" in r["why"], "a human disposes after the clock, and only then")

print("== the rack board ==")
rb = core.rack_board()
ok(rb["value"] > 0 and "rules_source" in rb, "the rack is counted with the rules named")
row = next((x for x in rb["rows"] if x.get("disposal_clock_days") is not None), None)
ok(row and "DATE ALERT" in row["label"], "disposal clocks are date alerts")

print("== rack sweep ==")
out = agents.rack_sweep()
ok(out["drafted"] >= 1, "aging orders get drafted reminders")

print("== matrix ==")
for a in ("deny_claim", "settle_off_schedule", "promise_stain_outcome", "dispose_before_clock"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("deny_claim", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a_["action"] == "deny_claim" and a_["state"] == "pending"
           for a_ in store.load("approvals")), "R0 never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no claim missed")
ok("ONE-STAR" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("rack_value" in r["recorded"], "rack value counted")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Ready-rack cash released"]["kind"] == "cash_timing", "rack cash is cash timing")
ok(labels["The claims file"]["kind"] == "scenario", "the claims file is a scenario")

print("== recovered, counted ==")
base = core.recovered_this_week()
o9["picked_up_at"] = iso(now() - timedelta(days=1))
store.upsert("orders", o9)
c9 = store.by_id("claims", "cl_demo_full")
c9["settled_at"] = iso(now())
store.upsert("claims", c9)
store.log_event("draft_rack_reminder", "or_demo_aging", "human:counter", "R1", {})
rec = core.recovered_this_week()
ok(rec["orders_picked_up"] == base["orders_picked_up"] + 1
   and rec["rack_cash_released"] >= 38, "released rack cash counted")
ok(rec["claims_settled"] == base["claims_settled"] + 1, "settled claims counted")
ok(rec["reminders_sent"] == 1, "human reminders counted; agent drafts are not")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
