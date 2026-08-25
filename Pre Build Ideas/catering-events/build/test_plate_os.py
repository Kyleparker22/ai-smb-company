#!/usr/bin/env python3
"""Plate OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["PLATEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="plateos-test-")
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
ok(core.read_message("one guest has a severe nut allergy")["label"] == "allergen",
   "an allergen note classifies")
ok(core.read_message("my mother is celiac, is the pasta station safe medically")["label"] == "allergen",
   "celiac classifies as allergen")
ok(core.read_message("can we swap the salmon entree for chicken")["label"] == "change_request",
   "a menu swap is a change request")
ok(core.read_message("final count is now 165, up from 150")["label"] == "change_request",
   "a count change is a change request")
ok(core.read_message("do you cater corporate holiday parties in december")["label"] == "inquiry",
   "an inquiry classifies")
ok(core.read_message("")["label"] == "human", "empty routes to a person")

ev = core.run_eval()
ok(ev["costly_label"] == "allergen" and ev["costly_missed"] == 0,
   f"zero missed allergen notes in the shipped eval ({ev['costly_missed']})")
ok("AMBULANCE" in ev["costly_note"], "the eval names the stake")

# ---------------------------------------------------------------- the lock window
locked = {"id": "e1", "date": iso(now() + timedelta(hours=40))}
chk = core.change_check(locked)
ok(chk["locked"] and "never auto-applied" in chk["refused"],
   "a change 40h out is inside the lock window")
open_ev = {"id": "e2", "date": iso(now() + timedelta(days=21))}
chk = core.change_check(open_ev)
ok(not chk["locked"], "a change 3 weeks out drafts normally")
past = {"id": "e3", "date": iso(now() - timedelta(days=2))}
ok(core.change_check(past)["locked"], "a past event cannot be changed")
ok(core.change_check({"id": "e4"}).get("refused"), "no date → nothing changed safely")

store.wipe()
store.save("config", {"company": "t"})
store.save("bookings", [locked, open_ev])
store.save("messages", [
    {"id": "m1", "booking_id": "e1", "text": "can we swap the salmon entree for chicken"},
    {"id": "m2", "booking_id": "e2", "text": "can we add a vegetarian entree option"},
])
r = agents.handle_message("m1")
ok(r["steps"][0]["action"] == "queue_locked_change", "the locked change queues for a human")
ok(any(e["detail"].get("action") == "auto_apply_locked_change"
       for e in store.events(kind="refused", subject="e1")), "the lock refusal is logged")
r = agents.handle_message("m2")
ok(r["steps"][0]["action"] == "draft_beo_change", "the open change drafts at R1")

# ---------------------------------------------------------------- the calendar
store.save("spaces", [{"id": "s1", "name": "The Barn", "capacity": 180}])
store.save("bookings", [{"id": "b1", "name": "wedding", "space_id": "s1",
                         "date": iso(now() + timedelta(days=10))}])
okb, why = core.can_book("s1", iso(now() + timedelta(days=10)), 100)
ok(not okb and "not a scheduling style" in why, "a booked date is refused")
okb, why = core.can_book("s1", iso(now() + timedelta(days=11)), 100)
ok(okb, "a free date books")
okb, why = core.can_book("s1", iso(now() + timedelta(days=11)), 300)
ok(not okb and "capacity" in why, "a capacity overrun refuses with the number")
r = agents.book("s1", iso(now() + timedelta(days=10)), 100)
ok("refused" in r and any(e["detail"].get("action") == "double_book_space"
                          for e in store.events(kind="refused")), "the conflict is logged")

# ---------------------------------------------------------------- final-count billing
e = {"id": "x", "final_count": 150, "per_head": 100,
     "additions": [{"desc": "bar hour", "amount": 800, "recorded_at": iso()},
                   {"desc": "verbal add", "amount": 600, "recorded_at": None}]}
inv = core.invoice(e)
ok(inv["total"] == 15800, "the bill = count × rate + recorded additions only")
ok(len(inv["excluded"]) == 1 and "dispute, not a charge" in inv["excluded"][0]["why"],
   "the unrecorded addition is excluded and named")
inv = core.invoice({"id": "y", "per_head": 100})
ok(inv.get("_missing") and "verbal number" in inv["_missing"],
   "no recorded final count → nothing can be billed")

# ---------------------------------------------------------------- R0 probes
for action in ("answer_allergen_question", "auto_apply_locked_change", "double_book_space",
               "bill_above_final_count"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("answer_allergen_question", "auto_apply_locked_change",
                           "double_book_space", "bill_above_final_count")
           for a in core.gate.pending()), "no R0 action reached the approval queue")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Inquiries answered inside an hour"]["value"] is None,
   "the inquiry line is blank without the operator's lift")
ok(labels["The allergen discipline"]["kind"] == "scenario",
   "the allergen discipline is never monetized")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("two vegans just rsvp'd, does the menu need anything", "change_request"),
                   ("bump the bar package to premium for the reception", "change_request"),
                   ("what's your availability for a 200 person gala this winter", "inquiry"),
                   ("my nephew has a dairy allergy, which passed apps are ok for him", "allergen")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

# ---------------------------------------------------------------- drafted copy
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

av = agents._availability_copy({"from": "Lena"})
ok("Lena" in av and "tasting" in av, "availability copy routes to the tasting")
ok("$" not in av, "no price by message — menus price per event")
booked = {"id": "bk9", "name": "Osei wedding", "starts_at": _iso(_now() + timedelta(hours=30))}
ack_locked = agents._change_ack_copy(booked, {"locked": True})
ok("nothing changes on paper" in ack_locked and "calls you" in ack_locked,
   "inside the window the ack promises a call, never an application")
ack_open = agents._change_ack_copy(booked, {"locked": False})
ok("drafted against the BEO" in ack_open and "confirm today" in ack_open,
   "outside the window the ack drafts and asks for confirmation")
ok("yourco" not in (av + ack_locked + ack_open).lower(),
   "white-label: no yourco name in outward copy")

# ---------------------------------------------------------------- recovered, counted
base = core.recovered_this_week()
store.log_event("draft_beo_change", "bk9", "human:eventlead", "R1", {})
store.log_event("draft_booking", "sp1", "human:owner", "R1", {})
rec = core.recovered_this_week()
ok(rec["changes_confirmed"] == base["changes_confirmed"] + 1
   and rec["bookings_made"] == base["bookings_made"] + 1,
   "human confirmations are counted; agent drafts are not")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
