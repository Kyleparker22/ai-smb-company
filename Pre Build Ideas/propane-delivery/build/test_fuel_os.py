#!/usr/bin/env python3
"""Fuel OS — the suite. `python3 test_fuel_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["FUELOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="fuelos_test_")
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
ok(len(store.load("tanks")) >= 300, "tanks seeded")

print("== triage: gas smell first ==")
for text, want in (("we smell gas in the basement by the water heater", "gas_smell"),
                   ("strong rotten egg odor in the kitchen since this morning", "gas_smell"),
                   ("there's a hissing sound at the tank regulator", "gas_smell"),
                   ("smelling propane in the crawl space", "gas_smell"),
                   ("we're out of gas and the furnace quit last night", "out_of_gas"),
                   ("the gauge reads zero and there's no heat", "out_of_gas"),
                   ("tank's empty, we ran out sometime yesterday", "out_of_gas"),
                   ("need a fill before the cold snap this weekend", "delivery"),
                   ("can you top off the tank when you're in the area", "delivery"),
                   ("what's your price per gallon right now", "price"),
                   ("what's my contract rate this season", "price"),
                   ("", "human"),
                   ("the driver was great, thanks", "human")):
    ok(core.read_call(text)["label"] == want, f"triage: {text[:42]} → {want}")

print("== the evacuate script ==")
out = agents.handle_call("cl_demo_smell")
step = out["steps"][0]
ok("leave the building NOW" in step["said"], "the script says leave now")
ok("do not touch light switches" in step["said"], "the script forbids switches")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "troubleshoot_gas_smell"
       for e in store.events()), "troubleshoot_gas_smell refused + logged")

print("== the leak-check gate ==")
out = agents.handle_call("cl_demo_outage")
ticket_id = out["steps"][0]["ticket"]
ok("leak check" in out["steps"][0]["draft"] and "non-negotiable" in out["steps"][0]["draft"],
   "the outage copy states the check as non-negotiable")
r = agents.close_outage(ticket_id)
ok("refused" in r and "houses\nexplode" in r["refused"] or "houses" in r["refused"],
   "no leak check → the ticket stays open, stake named")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "close_outage_without_leak_check"
       for e in store.events()), "close_outage_without_leak_check logged")
r = agents.close_outage(ticket_id, leak_result="pass — system tight", tech="T-Renner")
ok(r.get("closed"), "the recorded result closes it")
t = store.by_id("tickets", ticket_id)
ok(t["leak_check"]["tech"] == "T-Renner", "who ran the check is on the record")

print("== the contract clamp ==")
pf = core.price_for(store.by_id("customers", "cu_demo_contract"))
ok(pf["clamped"] and pf["per_gallon"] == 2.29, "the contract customer gets the contract price")
ok("cannot reach a contract customer" in pf["note"], "the clamp is named")
pf = core.price_for({})
ok(not pf.get("clamped") and pf["per_gallon"] == 2.89, "a market customer gets the posted price")
store.save("config", dict(store.load("config"), market_price=None))
pf = core.price_for({})
ok("_missing" in pf, "no recorded market price → no quote, never a guess")
store.save("config", dict(store.load("config"), market_price=2.89))
out = agents.handle_call("cl_demo_price")
ok("$2.29" in out["steps"][0]["draft"] and "that's your number" in out["steps"][0]["draft"],
   "the price copy speaks the contract")

print("== the requalification gate ==")
r = agents.fill_tank("tk_demo_expired")
ok("refused" in r and "requalified" in r["refused"], "expired requal → no fill")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "fill_unqualified_tank"
       for e in store.events()), "fill_unqualified_tank logged")
okf, why = core.can_fill_tank({"requal_due": None})
ok(not okf and "UNKNOWN is not" in why, "no date reads UNKNOWN — equally unfillable")
r = agents.fill_tank("tk_demo_ok")
ok(r.get("rung") == "R1" and r.get("approval"), "a current tank fills at R1")

print("== the runout board ==")
rb = core.runout_board()
ok(any(r.get("risk") == "critical" for r in rb), "critical tanks computed from usage")
ok(any(r.get("_missing") for r in rb), "history-less tanks read UNKNOWN, never fine")
out = agents.runout_sweep()
ok(out["alerts"] >= 1, "critical tanks raise alerts")

print("== matrix ==")
for a in ("troubleshoot_gas_smell", "close_outage_without_leak_check",
          "bill_contract_off_contract", "fill_unqualified_tank"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("troubleshoot_gas_smell", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no gas smell missed")
ok("EXPLODE" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("critical_tanks" in r["recorded"], "critical count recorded")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["The leak-check file"]["kind"] == "scenario",
   "a house that didn't explode is never a saving")

print("== recovered, counted ==")
rec = core.recovered_this_week()
ok(rec["outages_closed_with_checks"] >= 1, "closed-with-check outages counted")
store.log_event("draft_delivery", "tk_demo_ok", "human:dispatch", "R1", {})
rec = core.recovered_this_week()
ok(rec["deliveries_made"] == 1, "human deliveries counted; agent drafts are not")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
