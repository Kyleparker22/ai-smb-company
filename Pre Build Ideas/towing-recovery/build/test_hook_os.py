#!/usr/bin/env python3
"""Hook OS — the suite. `python3 test_hook_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["HOOKOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="hookos_test_")
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
ok(len(store.load("tows")) >= 200, "tows seeded")
ok(len(store.load("impounds")) >= 60, "impounds seeded")

print("== triage: rotation first ==")
for text, want in (("this is county dispatch, rotation tow at mile marker 12", "rotation"),
                   ("police on scene need a wrecker for a two-car accident", "rotation"),
                   ("trooper requesting rotation at the split", "rotation"),
                   ("car broke down on the shoulder of route 9", "breakdown"),
                   ("I'm stuck in a ditch off the county road", "breakdown"),
                   ("dead battery in the parking garage on level 3", "breakdown"),
                   ("how much is a tow across town", "price_question"),
                   ("what's your storage rate per day", "price_question"),
                   ("you impounded my car last night, where is it", "release_request"),
                   ("I need to come get my truck from your lot", "release_request"),
                   ("", "human"),
                   ("do you buy junk cars", "human")):
    ok(core.read_call(text)["label"] == want, f"triage: {text[:42]} → {want}")

print("== the rotation clock ==")
out = agents.handle_call("cl_demo_rotation")
ok(out["steps"][0]["action"] == "record_rotation_call", "rotation recorded at R2")
ok(any(e["kind"] == "record_rotation_call" for e in store.events()), "the record lands in the log")
ok(any(a["action"] == "draft_dispatch" for a in store.load("approvals")),
   "the truck assignment queues in the same breath")

print("== the rate-card clamp ==")
inv = core.tow_invoice({"miles": 10})
card = core.rate_card()
ok(inv["total"] == card["hookup"] + 10 * card["per_mile"], "invoice computes from the card")
ok("no other number exists" in inv["basis"], "the basis names the clamp")
ok("_missing" in core.tow_invoice({}), "no mileage → cannot be priced, never guessed")
r = agents.bill_tow("tw_demo_over")
ok("refused" in r and "exceeds the filed-card total" in r["refused"],
   "$900 request clamped with both numbers shown")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "charge_above_rate_card"
       for e in store.events()), "charge_above_rate_card logged")
r = agents.bill_tow("tw_demo_clean")
ok(r.get("gate", {}).get("rung") == "R1", "clean tow bills from the card at R1")

print("== the damage evidence pair ==")
v = agents.damage_dispute("tw_demo_nophotos")
ok(not v["assertable"] and "1 hookup photo" in v["refused"],
   "one photo → cannot assert either way")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "assert_no_damage_without_photos"
       for e in store.events()), "the refusal is logged")
v = agents.damage_dispute("tw_demo_clean")
ok(v["assertable"] and v["photos"] == 5, "the photo set does the arguing")

print("== storage arithmetic ==")
imp = {"impounded_at": iso(now() - timedelta(days=5))}
sb = core.storage_bill(imp)
ok(sb["days"] in (5, 6) and sb["total"] == sb["days"] * core.rate_card()["storage_per_day"],
   "storage computes from the stamp to today")
imp["released_at"] = iso(now() - timedelta(days=2))
sb2 = core.storage_bill(imp)
ok(sb2["days"] in (3, 4) and "recorded release" in sb2["ends_at"],
   "the meter stops at the recorded release")
ok("_missing" in core.storage_bill({}), "no impound stamp → nothing billed")

print("== the lien calendar ==")
cal = core.lien_calendar(store.by_id("impounds", "im_demo_aging"))
ok(cal.get("steps") and cal["steps"][0]["label"] == "DATE ALERT — not legal advice",
   "lien steps are date alerts")
ok("DEFAULT rule set" in cal["rules_source"], "the rules name themselves replaceable")
ok("_missing" in core.lien_calendar({"state_code": "ZZ", "impounded_at": iso(now())}),
   "an unknown state refuses, never guesses")
out = agents.lien_sweep()
ok(out["alerts"] >= 1, "aging impounds raise date alerts")

print("== drafted copy ==")
pc = agents._price_copy()
ok(f"${card['hookup']}" in pc and "filed with the city" in pc, "price copy is the card, cited")
rl = agents._release_copy({"from": "Renner"})
ok("meter stops the moment" in rl and "photo ID" in rl, "release copy states the meter rule")
ok("yourco" not in (pc + rl).lower(), "white-label")

print("== matrix ==")
for a in ("charge_above_rate_card", "assert_no_damage_without_photos", "file_lien",
          "sell_vehicle", "backdate_release"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("sell_vehicle", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a_["action"] == "sell_vehicle" and a_["state"] == "pending"
           for a_ in store.load("approvals")), "R0 never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no rotation call missed")
ok("minutes" in ev["costly_note"].lower(), "costly note names the clock")

print("== roi ==")
r = core.roi({})
ok("held_storage_value" in r["recorded"], "held storage recorded")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["The rate-card defense file"]["kind"] == "scenario", "the defense is a scenario")

print("== recovered, counted ==")
base = core.recovered_this_week()
i9 = store.by_id("impounds", "im_demo_aging")
i9["released_at"] = iso(now() - timedelta(days=1))
store.upsert("impounds", i9)
rec = core.recovered_this_week()
ok(rec["vehicles_released"] == base["vehicles_released"] + 1, "a release is counted")
ok(rec["rotation_calls"] >= 1, "rotation calls counted from the log")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
