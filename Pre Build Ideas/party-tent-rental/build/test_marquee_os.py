#!/usr/bin/env python3
"""Marquee OS — the suite. `python3 test_marquee_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["MARQUEEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="marqueeos_test_")
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
ok(len(store.load("bookings")) >= 50, "bookings seeded (~50 across two weekends)")
ok(len(store.load("inventory")) >= 7, "inventory counted by item type")
ok(len(store.load("messages")) >= 15, "messages seeded")
first_event_id = store.events()[0]["id"]

print("== triage: the weather worry reads first ==")
for text, want in (("they're calling for 50mph gusts saturday, is the tent safe", "weather_worry"),
                   ("storm coming during the reception, will the tent hold up", "weather_worry"),
                   ("forecast says high winds for our event, should we be worried", "weather_worry"),
                   ("it's supposed to thunderstorm sunday, is the 40x60 going to be okay", "weather_worry"),
                   ("wind rating question — what are your tents rated for", "weather_worry"),
                   ("do you have a 40x60 tent available the first weekend of june", "booking_request"),
                   ("need 200 chairs and 20 round tables for a graduation party", "booking_request"),
                   ("can we add a dance floor to our order", "change_request"),
                   ("we need to move our tent order to the following saturday", "change_request"),
                   ("when do we get our deposit back", "deposit_ask"),
                   ("you charged our deposit for a stain we didn't make", "deposit_ask"),
                   ("what time is the crew arriving friday", "status"),
                   ("is our order confirmed for the 14th", "status"),
                   ("", "human"),
                   ("do you do fireworks too", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

print("== the wind call: numbers stated, a human named, no reassurance ==")
out = agents.handle_message("ms_demo_gust")
step = out["steps"][0]
draft = step["draft"]
ok(step["action"] == "draft_weather_note", "the wind worry drafts a weather note")
ok("50" in draft and "40 mph" in draft, "the draft states the numbers: forecast 50 vs rated 40")
ok("exceeds the rated limit" in draft, "the draft says plainly that the forecast exceeds the limit")
ok("crew chief" in draft, "a person is named as the one who makes the call")
ok("belongs" in draft and "not to software" in draft, "the draft says software does not decide")
ok(core.tone_ok(draft)[0], "the shipped copy passes the tone check structurally")
ok(not core.tone_ok("relax, it'll be fine, the tent is totally safe")[0],
   "reassurance language is structurally refused")
ok(not core.tone_ok("don't worry, rest assured it is perfectly safe")[0],
   "soothing language is structurally refused")
ok("yourco" not in draft.lower(), "white-label: no yourco in the weather draft")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "make_weather_call"
       for e in store.events()), "make_weather_call refused + logged on the wind message")

print("== make_weather_call is R0, never promotable, never approvable ==")
r = core.weather_call("bk_demo_gust")
ok(r.get("refused") and r.get("rung") == "R0", "the software probe is refused at R0")
ok(not any(a["action"] == "make_weather_call" and a["state"] == "pending"
           for a in store.load("approvals")), "R0 never becomes an approvable row")
r = core.weather_call("bk_demo_gust", human="crew_chief_dana", decision="hold",
                      note="re-check at 6am")
ok(r.get("recorded") and r["by"] == "crew_chief_dana", "a named human records the call")
ok("50" in (r.get("wind") or ""), "the recorded call carries the numbers")
b9 = store.by_id("bookings", "bk_demo_gust")
ok((b9.get("weather_call") or {}).get("decision") == "hold", "the call lands on the booking record")
r = core.weather_call("bk_demo_gust", human="crew_chief_dana", decision="wing it")
ok(r.get("refused"), "an unrecognized decision does not record — refused, not coerced")

print("== oversell is structurally impossible ==")
cap = core.capacity_board()
w2 = cap["weekends"][-1]["weekend"]
av_before = core.availability(w2)
ok(av_before["tent_40x60"]["available"] == 0, "the crunch weekend has zero 40x60s left")
stock_before = {i["id"]: i["stock"] for i in store.load("inventory")}
reserved_before = core.reserved_for_weekend(w2)
r = core.reserve("Walk-in", w2, {"tent_40x60": 1}, demo_tag="demo")
ok(r["status"] == "waitlisted", "reserving past the count waitlists — never oversells")
ok("tent_40x60" in (r["short"] or {}), "the short item is named")
ok("nothing was taken from another event" in r["why"], "the waitlist claim is honest")
ok({i["id"]: i["stock"] for i in store.load("inventory")} == stock_before,
   "inventory counts unchanged by the waitlisted attempt")
ok(core.reserved_for_weekend(w2) == reserved_before,
   "reserved counts unchanged — a waitlisted booking holds nothing")
w1 = cap["weekends"][0]["weekend"]
av1 = core.availability(w1)["tent_40x60"]["available"]
ok(av1 >= 1, "weekend one still has a 40x60 counted available")
r = core.reserve("Kowalski", w1, {"tent_40x60": 1}, demo_tag="demo")
ok(r["status"] == "confirmed", "a reservation inside the count confirms")
ok(core.availability(w1)["tent_40x60"]["available"] == av1 - 1,
   "a confirmed reservation moves the counted availability")
r = core.reserve("Walk-in", w1, {"tent_99x99": 1})
ok("refused" in r and "tent_99x99" in r["refused"], "an uncounted item cannot be promised")

print("== the 811 wall ==")
r = agents.install("bk_demo_no811")
ok("refused" in r and "811" in r["refused"], "install without the recorded 811 ticket refused")
ok("wall" in r["refused"], "the refusal names the wall, not a checkbox")
ok(any(e["kind"] == "refused"
       and (e["detail"] or {}).get("action") == "install_without_utility_locate"
       for e in store.events()), "install_without_utility_locate logged")
r = agents.install("bk_demo_gust")
ok(r.get("cleared") and "811-2026-5117" in r["why"], "with the ticket on record, the checklist clears")
ok("human dispatch" in r["note"], "the truck still rolls on a human dispatch")

print("== deposit math needs both condition records ==")
r = agents.settle_deposit("bk_demo_dep_partial")
ok("refused" in r and "return-condition record" in r["refused"],
   "missing return record → refused with the missing record named")
ok("out-condition" not in r["refused"].split("missing:")[1].split(".")[0],
   "only the actually-missing record is named")
ok(any(e["kind"] == "refused"
       and (e["detail"] or {}).get("action") == "deduct_deposit_without_condition_records"
       for e in store.events()), "deduct_deposit_without_condition_records logged")
r = agents.settle_deposit("bk_demo_dep_full")
ok(r["math"]["deduction"] == 150, "the deduction is the condition pair's arithmetic")
ok(r["math"]["refund"] == 350, "refund = deposit − recorded new damage")
ok(all(d["item"] != "chair scuffs (pre-existing)" for d in r["math"]["new_damage"]),
   "pre-existing damage on the out record is never charged")
ok(r["action"] == "draft_deposit_deduction" and r["gate"]["rung"] == "R1",
   "the deduction drafts at R1 — a human sends")
ok(r["math"]["evidence"]["out"] == "cd_out_full" and r["math"]["evidence"]["return"] == "cd_ret_full",
   "both condition records are referenced as evidence")
r = agents.settle_deposit("bk_demo_dep_clean")
ok(r["action"] == "draft_deposit_refund" and r["math"]["refund"] == 500,
   "a clean return drafts the full refund — still R1, still from the pair")
ok("yourco" not in str(r["math"]).lower(), "white-label: no yourco in the deposit math")

print("== permit clocks are DATE ALERTS ==")
pb = core.permit_board()
ok("DEFAULT" in pb["rules_source"] and "not legal advice" in pb["rules_source"],
   "the permit table names itself a DEFAULT and not legal advice")
row = next((x for x in pb["rows"] if x["booking"] == "bk_demo_permit"), None)
ok(row and row.get("permit") == "NOT FILED", "the unfiled Belmont permit is surfaced")
ok(row and "DATE ALERT" in (row.get("label") or ""), "the clock is a DATE ALERT, filing a human act")
muni_row = next((x for x in pb["rows"] if x["booking"] == "bk_demo_muni"), None)
ok(muni_row and muni_row.get("_missing") and "Kern Township" in muni_row["_missing"],
   "a municipality with no recorded rule is named, never defaulted")
filed = [x for x in pb["rows"] if x.get("permit") == "filed"]
ok(len(filed) >= 1 and all(f.get("permit_ref") for f in filed), "filed permits carry their ref")

print("== permit sweep skips demo fixtures ==")
sw = agents.permit_sweep()
ok(not any(e["kind"] in ("permit_alert", "queued_for_approval") and e["subject"] == "bk_demo_permit"
           for e in store.events()), "the sweep never performs on demo_tag rows")

print("== matrix ==")
for a in ("make_weather_call", "oversell_inventory", "install_without_utility_locate",
          "deduct_deposit_without_condition_records"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("oversell_inventory", "probe", "x", {})
ok(r.get("refused"), "the oversell probe is refused at R0 (and the real path has no code for it)")
ok(not any(a["action"] in ("oversell_inventory", "install_without_utility_locate")
           and a["state"] == "pending" for a in store.load("approvals")),
   "no R0 action ever becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no weather worry missed")
ok("A STAKED TENT IN WIND KILLS" in ev["costly_note"], "the costly note names the stake, in caps")

print("== roi ==")
r = core.roi({})
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok("idle_weekend_value" in r["recorded"], "the idle weekend value is counted, not asked for")
labels = {l["label"]: l for l in r["lines"]}
ok(labels["Deposit disputes avoided"]["kind"] == "scenario", "deposit disputes are a scenario")
ok(labels["Deposit disputes avoided"]["value"] is None
   and "_missing" in labels["Deposit disputes avoided"],
   "a scenario with no operator input renders blank with a reason — never estimated")
ok(labels["Permit fines & shut-downs"]["kind"] == "scenario", "permit fines are a scenario")
ok(labels["Office & phone hours"]["kind"] == "time_saved", "office hours are time_saved, never revenue")

print("== recovered, counted (a draft is not a send) ==")
base = core.recovered_this_week()
store.log_event("draft_booking_reply", "ms_000", "agent:desk", "R1", {})
mid = core.recovered_this_week()
ok(mid["replies_sent"] == base["replies_sent"], "an agent's draft does not count as a send")
store.log_event("draft_booking_reply", "ms_000", "human:owner", "R1", {})
store.log_event("draft_deposit_refund", "bk_demo_dep_clean", "human:owner", "R1", {})
rec = core.recovered_this_week()
ok(rec["replies_sent"] == base["replies_sent"] + 1, "a human send counts — baseline delta")
ok(rec["deposit_actions_sent"] == base["deposit_actions_sent"] + 1, "human deposit actions counted")
ok(rec["bookings_confirmed"] >= 1, "bookings confirmed this week are counted from the book")
ok("counted" in rec["note"] and "draft is not a send" in rec["note"],
   "recovered names its basis")

print("== the append-only log ==")
n1 = len(store.events())
agents.handle_message("ms_demo_book")
n2 = len(store.events())
ok(n2 > n1, "every action appends events")
ok(store.events()[0]["id"] == first_event_id, "the first event is still first — nothing rewritten")
bk = next((b for b in store.load("bookings") if b.get("customer_name") == "Kowalski"
           and b.get("status") == "waitlisted"), None)
ok(bk is not None, "the demo booking request waitlisted honestly (the weekend is full)")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a),
   "automation counted from the log, or refused with a reason")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
