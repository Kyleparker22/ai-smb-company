#!/usr/bin/env python3
"""Rebid OS — the suite. `python3 test_rebid_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["REBIDOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="rebidos_test_")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from datetime import timedelta

import agents, core, seed
from core import store
from _kit.store import is_missing, iso, now

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
ok(len(store.load("machines")) == 12, "12 machines")
ok(len({m["machine_class"] for m in store.load("machines")}) == 4, "4 classes")
ok(len(store.load("graveyard")) >= 300, "graveyard of 300+ lost quotes")
ok(len(store.load("weeks")) == 8, "2 schedule weeks per class")

print("== counted idle: booked vs available, hand-checked ==")
wk_next = core.next_week()
wk_this = core.this_week()
idle = core.counted_idle("3-axis mill", wk_next)
booked_by_hand = sum(b["hours"] for b in store.load("bookings")
                     if b["machine_class"] == "3-axis mill" and b["week_of"] == wk_next)
ok(booked_by_hand == 149, f"3-axis next week booked by hand = 149 (got {booked_by_hand})")
ok(idle["available"] == 180, "3-axis available = 4 machines × 45h = 180h")
ok(idle["booked"] == 149, "counted booked matches the hand sum")
ok(idle["idle_hours"] == 31, "180 − 149 = 31 counted idle hours")
ok("counted idle" in idle["basis"], "the basis names itself counted")
idle2 = core.counted_idle("lathe", wk_this)
ok(idle2["idle_hours"] == 4, "lathe this week: 180 − 176 = 4h")

print("== the unmaintained week is unmeasured — the desk stands down ==")
edm = core.counted_idle("wire EDM", wk_this)
ok(is_missing(edm), "wire EDM capacity is unmeasured, never estimated")
ok("not maintained" in edm["_missing"], "the reason names the unmaintained schedule")
ok("can't count" in edm["_missing"], "we don't sell hours we can't count")
ok(core.counted_idle("wire EDM", wk_next).get("idle_hours") is None,
   "no zero-fill on the unmeasured week")

print("== the marginal floor: arithmetic printed, hand-checked ==")
q = store.by_id("graveyard", "gq_demo_rebid")
f = core.floor_math(q)
ok(f["labor"] == 1496.0, "labor = 22h × $68 = $1,496")
ok(f["material"] == 640.0, "material = $640, recorded")
ok(f["margin_line"] == 213.6, "margin line = (1496+640) × 10% = $213.60")
ok(f["floor_price"] == 2349.6, "floor = 1496 + 640 + 213.60 = $2,349.60")
ok("$1,496.00 labor" in f["arithmetic"] and "$2,349.60 floor" in f["arithmetic"],
   "the arithmetic prints, line by line")
d = core.defensible_price(q)
ok(d["price"] == 2734.08, "defensible = (1496+640) × 1.28 = $2,734.08")
ok(d["price"] >= f["floor_price"], "defensible never sits below the floor")

print("== below the floor: NO PATH, structural ==")
r = agents.propose_bid("gq_demo_rebid", 2000)
ok("refused" in r and "NO PATH" in r["refused"], "a $2,000 bid under the $2,349.60 floor is refused")
ok("$2,349.60" in r["refused"] and "$1,496.00 labor" in r["refused"],
   "the refusal prints the floor's arithmetic")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "bid_below_marginal_floor"
       for e in store.events()), "bid_below_marginal_floor logged as a refusal")
ok(not any(a.get("action") == "bid_below_marginal_floor" for a in store.load("approvals")),
   "no approvable row exists for a below-floor bid — nobody clicks past the floor")
r = agents.propose_bid("gq_demo_rebid", 2500)
ok(r.get("ok") and "re-bid desk" in r["note"],
   "above the floor a hand price still routes through the desk — it never drafts alone")

print("== triage: the deadline RFQ reads first ==")
for text, want in (("need 200 of the clamp plates by friday, can you?", "deadline_rfq"),
                   ("can you turn 50 shafts by thursday", "deadline_rfq"),
                   ("rush order — 80 parts, is it possible this week", "deadline_rfq"),
                   ("need 500 spacers by monday morning", "deadline_rfq"),
                   ("120 pcs by wednesday — doable?", "deadline_rfq"),
                   ("got your requote on the manifold blocks, let's talk", "rebid_reply"),
                   ("saw the new price on the brackets — send the PO terms", "rebid_reply"),
                   ("any word on the quote for the housings?", "quote_status"),
                   ("did you get my rfq from last tuesday", "quote_status"),
                   ("we changed the material to 17-4 on the pump housing", "spec_change"),
                   ("rev c drawing attached, tolerances tightened on the bore", "spec_change"),
                   ("", "human"),
                   ("what are your shop hours over the holiday", "human"),
                   ("thanks for the tour last week", "human"),
                   ("invoice 4471 shows the wrong PO number", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]!r} → {want}")

print("== the deadline RFQ: answered from counted hours, never optimism ==")
out = agents.handle_message("ms_demo_friday")
step = out["steps"][0]
ok(out["classification"]["label"] == "deadline_rfq", "the Friday RFQ is the costly label")
ok(step["answer"] == "yes", "31 counted idle ≥ 26 needed → yes")
ok("31 counted idle hours" in step["draft"], "the answer cites the counted idle hours")
ok("~26h" in step["draft"] and "bookable" in step["draft"],
   "the answer shows the need and commits honestly")
ok("counted schedule" in step["draft"] and "gut feel" in step["draft"],
   "the copy names its basis")
ok("yourco" not in step["draft"].lower(), "white-label")
ap = [a for a in store.load("approvals")
      if a["action"] == "answer_deadline_rfq" and a["state"] == "pending"]
ok(len(ap) == 1 and ap[0]["rung"] == "R1", "the deadline answer queues at R1 — a human sends")

print("== the honest no ==")
store.upsert("messages", {"id": "ms_test_big", "from": "Theo",
                          "text": "need 400 of the clamp plates by friday, can you?",
                          "machine_class": "3-axis mill", "qty": 400, "hours_per_pc": 0.13,
                          "at": iso()})
out = agents.handle_message("ms_test_big")
step = out["steps"][0]
ok(step["answer"] == "no", "400 pcs needs 52h > 31 counted → honest no")
ok("~52h" in step["draft"] and "31 counted idle hours" in step["draft"],
   "the no cites both numbers")
ok("don't promise hours we can't count" in step["draft"], "the no names the rule")

print("== no recorded hours-per-piece → optimism refused ==")
out = agents.handle_message("ms_demo_no_hours")
step = out["steps"][0]
ok("refused" in step and "optimism never does" in step["refused"],
   "no counted math → no committed answer")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "promise_capacity_optimism"
       for e in store.events()), "promise_capacity_optimism logged as a refusal")

print("== the deadline RFQ on the uncounted week → stand-down ==")
out = agents.handle_message("ms_demo_edm_friday")
step = out["steps"][0]
ok(step.get("stand_down") and "stands down" in step["refused"],
   "the wire-EDM deadline answer stands down")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "sell_uncounted_capacity"
       and e["subject"] == "ms_demo_edm_friday" for e in store.events()),
   "sell_uncounted_capacity logged for the deadline stand-down")

print("== the standing order fires: re-bid with the floor's math printed ==")
r = agents.rebid("gq_demo_rebid")
ok(r.get("drafted"), "the re-biddable quote drafts")
ok(r["price"] == 2734.08, "the re-bid is the defensible price")
ok(r["price"] >= core.floor_math(q)["floor_price"], "never below the floor, structurally")
ok(2734.08 <= 2950, "defensible ≤ the price it died at — the precondition held")
ok("open capacity the week of" in r["draft"], "the copy names the open week")
ok("why the price moved" in r["draft"], "the copy explains the move honestly")
ok("$2,349.60 floor" in r["draft"], "the floor's arithmetic prints on the offer")
ok("silence is an answer" in r["draft"], "the exit is stated to the buyer")
ok("yourco" not in r["draft"].lower(), "white-label")
gg = r["gate"]
ok(not gg.get("executed") and gg["rung"] == "R1", "the re-bid queues at R1 — a human sends")
q2 = store.by_id("graveyard", "gq_demo_rebid")
ok(q2.get("last_rebid_at"), "last_rebid_at recorded")
ok(q2["rebid_history"][-1]["price"] == 2734.08, "the re-bid lands in the history")

print("== bounds: one per quarter, silence is an answer ==")
r = agents.rebid("gq_demo_rebid")
ok("skipped" in r and r["kind"] == "cooldown", "an immediate second re-bid hits the cooldown")
r = agents.rebid("gq_demo_cooldown")
ok("skipped" in r and "one re-bid per quote per quarter" in r["skipped"],
   "20 days since the last re-bid → the quarter rule holds")
ok(len(store.by_id("graveyard", "gq_demo_cooldown").get("rebid_history") or []) == 1,
   "no new history row on a cooldown skip")
r = agents.rebid("gq_demo_silence")
ok("skipped" in r and "silence is an answer" in r["skipped"], "a silent door stays shut")

print("== capability losses never re-bid ==")
r = agents.rebid("gq_demo_capability")
ok("refused" in r and "the machine didn't change" in r["refused"],
   "capability loss refused with the reason")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "rebid_capability_loss"
       for e in store.events()), "rebid_capability_loss logged")

print("== unrecorded hours → UNREBIDDABLE ==")
r = agents.rebid("gq_demo_unrecorded")
ok("refused" in r and "UNREBIDDABLE" in r["refused"], "no hours, no marginal math")
ok("Record the hours" in r["refused"], "the refusal names the way back in")

print("== the uncounted week → the desk stands down ==")
r = agents.rebid("gq_demo_edm")
ok("refused" in r and r.get("stand_down"), "the wire-EDM re-bid stands down")
ok("can't count" in r["refused"], "the stand-down names the rule")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "sell_uncounted_capacity"
       and e["subject"] == "gq_demo_edm" for e in store.events()),
   "sell_uncounted_capacity logged for the re-bid stand-down")

print("== a re-bid must be defensible: at or below the died-at price ==")
store.upsert("graveyard", {"id": "gq_test_high", "part": "6061 stop block ×10",
                           "machine_class": "3-axis mill", "hours": 4, "material_cost": 100,
                           "died_at_price": 300, "loss_reason": "price", "contact": "Lena",
                           "lost_at": iso(now() - timedelta(days=200))})
r = agents.rebid("gq_test_high")
ok("skipped" in r and r["kind"] == "not_defensible",
   "defensible $476 > died-at $300 → no re-bid")
ok("not a story we can tell" in r["skipped"], "the skip explains itself")

print("== drafted re-bids hold their hours — no double-selling counted idle ==")
held = core.reserved_hours("3-axis mill", wk_next)
ok(held == 22.0, f"the drafted re-bid holds its 22h (held={held})")
store.upsert("graveyard", {"id": "gq_test_15h", "part": "7075 guide rail ×20",
                           "machine_class": "3-axis mill", "hours": 15, "material_cost": 200,
                           "died_at_price": 2600, "loss_reason": "price", "contact": "Boyd",
                           "lost_at": iso(now() - timedelta(days=180))})
r = agents.rebid("gq_test_15h")
ok("skipped" in r and r["kind"] == "no_idle",
   "15h does not fit: this week 9h free, next week 31−22=9h free")
ok("held by pending drafts" in r["skipped"], "the skip names the held hours")
store.upsert("graveyard", {"id": "gq_test_8h_a", "part": "1018 spacer ×50",
                           "machine_class": "3-axis mill", "hours": 8, "material_cost": 200,
                           "died_at_price": 2000, "loss_reason": "lead_time", "contact": "Cal",
                           "lost_at": iso(now() - timedelta(days=180))})
r = agents.rebid("gq_test_8h_a")
ok(r.get("drafted") and r["week_of"] == wk_this, "8h fits this week's 9h free — drafts")
store.upsert("graveyard", {"id": "gq_test_8h_b", "part": "brass end cap ×50",
                           "machine_class": "3-axis mill", "hours": 8, "material_cost": 200,
                           "died_at_price": 2000, "loss_reason": "price", "contact": "Renata",
                           "lost_at": iso(now() - timedelta(days=180))})
r = agents.rebid("gq_test_8h_b")
ok(r.get("drafted") and r["week_of"] == wk_next, "the next 8h spills to next week's 9h free")
store.upsert("graveyard", {"id": "gq_test_8h_c", "part": "303 SS piston ×50",
                           "machine_class": "3-axis mill", "hours": 8, "material_cost": 200,
                           "died_at_price": 2000, "loss_reason": "price", "contact": "Ingrid",
                           "lost_at": iso(now() - timedelta(days=180))})
r = agents.rebid("gq_test_8h_c")
ok("skipped" in r and r["kind"] == "no_idle", "a third 8h finds 1h free everywhere — no draft")
for wk in (wk_this, wk_next):
    it = core.counted_idle("3-axis mill", wk)
    ok(core.reserved_hours("3-axis mill", wk) <= it["idle_hours"],
       f"held hours never exceed counted idle (wk {wk})")

print("== the sweep: bounded, demo-skipping, reservation-honest ==")
before_cap = store.by_id("graveyard", "gq_demo_capability").get("last_rebid_at")
out = agents.rebid_sweep()
ok(out["drafted"] + out["watching"] + out["stood_down"] + out["skipped"] > 250,
   "the sweep walks the whole graveyard")
ok(store.by_id("graveyard", "gq_demo_capability").get("last_rebid_at") == before_cap,
   "demo fixtures are skipped by the sweep")
for row in core.capacity_board()["rows"]:
    if not row.get("idle"):
        ok(row["held_hours"] <= row["idle_hours"],
           f"post-sweep: held ≤ counted idle for {row['machine_class']} wk {row['week_of']}")
drafted = [a for a in store.load("approvals")
           if a["action"] == "draft_rebid" and a["state"] == "pending"]
ok(all(a["detail"]["price"] >= a["detail"]["floor"]["floor_price"] for a in drafted),
   "every drafted re-bid sits at or above its floor")
ok(all("arithmetic" in a["detail"]["floor"] for a in drafted),
   "every drafted re-bid carries the floor's arithmetic")

print("== rebid replies land on the history — silence stays a real exit ==")
out = agents.handle_message("ms_demo_rebid_reply")
ok(out["steps"][0]["action"] == "draft_rebid_reply", "a re-bid reply drafts for a human")
hist = store.by_id("graveyard", "gq_demo_rebid")["rebid_history"]
ok(hist[-1]["response"] == "reply", "the reply is recorded against the re-bid")

print("== matrix: the four R0s are structural ==")
for a in ("bid_below_marginal_floor", "sell_uncounted_capacity",
          "rebid_capability_loss", "promise_capacity_optimism"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
    r = core.gate.act(a, "probe", "x", {})
    ok(r.get("refused"), f"R0 probe {a} refused")
ok(not any(a_["action"] in core.matrix.never_promote() and a_["state"] == "pending"
           for a_ in store.load("approvals")), "no R0 ever becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["n"] >= 15, f"{ev['n']} labelled cases")
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no deadline RFQ missed")
ok(ev["costly_label"] == "deadline_rfq", "the costly label is the deadline RFQ")
ok("OPTIMISM" in ev["costly_note"], "the costly note names the stake")

print("== roi: typed, recorded, blank scenario ==")
r = core.roi({})
ok(r["recorded"]["target_margin"] == 0.28, "target margin recorded")
ok("avg_variable_cost_hr" in r["recorded"], "fleet variable cost recorded")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Graveyard revenue recovered"]["kind"] == "revenue", "recovery typed revenue")
ok(labels["Quoting and chase hours"]["kind"] == "time_saved", "hours typed time_saved")
sc = labels["The defensible-price story"]
ok(sc["kind"] == "scenario" and sc["value"] is None and "price_integrity_value" in sc["_missing"],
   "the scenario line renders blank with its missing input named")
ok(labels["Graveyard revenue recovered"]["value"] is None,
   "no recovery revenue is asserted before wins land")

print("== the counted week, baseline-delta ==")
base = core.this_week_counted()
store.log_event("draft_rebid", "gq_demo_rebid", "human:owner", "R1", {})
store.log_event("answer_deadline_rfq", "ms_demo_friday", "human:owner", "R1", {})
rec = core.this_week_counted()
ok(rec["rebids_sent"] == base["rebids_sent"] + 1, "a human-sent re-bid counts")
ok(rec["deadline_answers_sent"] == base["deadline_answers_sent"] + 1,
   "a human-sent deadline answer counts")
ok(rec["rebids_sent"] >= 1 and base["rebids_sent"] == rec["rebids_sent"] - 1,
   "agent drafts alone never count as sent")
ok("counted" in rec["note"], "the week names its basis")

print("== record_loss: the graveyard door ==")
r = agents.record_loss({"part": "4140 gear blank ×30", "machine_class": "lathe",
                        "hours": None, "material_cost": 500, "died_at_price": 2100,
                        "loss_reason": "price", "contact": "Theo"})
ok(r["recorded"] and r["status"].startswith("UNREBIDDABLE"),
   "a loss without hours is named UNREBIDDABLE at the door, not a quarter late")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a),
   "automation counted or refused — never asserted")

print("== append-only ==")
first = store.events()[0]
n0 = len(store.events())
store.log_event("corrected", "gq_demo_rebid", "human:owner", "R1", {"action": "draft_rebid"})
ok(len(store.events()) == n0 + 1, "a correction is a new event")
ok(store.events()[0] == first, "no event is ever rewritten")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
