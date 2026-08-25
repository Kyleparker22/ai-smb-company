#!/usr/bin/env python3
"""Lot OS — the suite. `python3 test_lot_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["LOTOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="lotos_test_")
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
ok(len(store.load("units")) >= 140, "units seeded")

print("== triage: the lead reads first ==")
for text, want in (("is the blue civic still available", "lead"),
                   ("saw your listing for the f-150, interested", "lead"),
                   ("can we come test drive the camry saturday", "lead"),
                   ("still available? the white suv", "lead"),
                   ("what would payments be with 2k down", "payment_ask"),
                   ("how much a month would the tahoe run me", "payment_ask"),
                   ("what's my 2018 accord worth on trade", "trade_ask"),
                   ("what would you give me for my truck", "trade_ask"),
                   ("has the altima been in an accident", "condition_ask"),
                   ("does the carfax show anything on the wrangler", "condition_ask"),
                   ("", "human"),
                   ("what time do you close today", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:42]} → {want}")

print("== the condition rule ==")
cs = core.condition_statement(store.by_id("units", "un_demo_report"))
ok("AutoRecord report dated" in cs["statement"] and "rear impact" in cs["statement"],
   "with a report the statement cites source, date, and the record's own words")
ok("'Never wrecked' is not expressible" in cs["note"], "the rule is named")
cs = core.condition_statement(store.by_id("units", "un_demo_noreport"))
ok("refused" in cs and "copy stays silent" in cs["refused"], "no report → no condition copy")
out = agents.handle_message("ld_demo_cond")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "assert_condition_beyond_record"
       for e in store.events()), "assert_condition_beyond_record logged")

print("== payment discipline ==")
pq = core.payment_quote(store.by_id("deals", "dl_demo_titled"))
ok(pq.get("monthly") and 250 < pq["monthly"] < 350, "payment computes from recorded terms")
ok("8.9% APR" in pq["disclosure"] and "on approved credit" in pq["disclosure"],
   "the disclosure rides with the number")
pq = core.payment_quote({})
ok("refused" in pq and "unlicensed finance quote" in pq["refused"],
   "no terms → no number, stake named")
out = agents.handle_message("ld_demo_pay")
ok(out["steps"][0]["action"] == "invite_finance_conversation",
   "the reply invites the conversation instead")
ok("$" not in out["steps"][0]["draft"] or "real numbers in writing" in out["steps"][0]["draft"],
   "no invented figure in the reply")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "quote_payment_without_terms"
       for e in store.events()), "quote_payment_without_terms logged")

print("== the title gate ==")
r = agents.mark_delivered("dl_demo_notitle")
ok("refused" in r and "brings the state in" in r["refused"], "no title status → no delivery")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "deliver_without_title_status"
       for e in store.events()), "deliver_without_title_status logged")
r = agents.mark_delivered("dl_demo_titled")
ok(r.get("rung") == "R1" and r.get("approval"), "titled deal queues at R1")

print("== trade bands ==")
b = core.trade_band("accord")
ok(b.get("band") and b["band"][0] <= b["band"][1], "enough book history → a band")
b = core.trade_band("miata")
ok("_missing" in b and "costs real money on both sides" in b["_missing"],
   "thin book → refused with the reason")
out = agents.handle_message("ld_demo_trade")
ok("$" in out["steps"][0]["draft"] and "eyes on the car" in out["steps"][0]["draft"],
   "the accord gets the honest band copy")

print("== the aged board ==")
store.upsert("units", {"id": "un_aged", "desc": "2018 F-150 XLT",
                       "acquired_at": iso(now() - timedelta(days=95))})
aged = core.aged_board()
row = next(r for r in aged if r["unit"] == "un_aged")
ok(row["bucket"] == "90+" and row["interest_accrued"] > 800,
   "a 95-day unit shows its bucket and accrued dollars")
store.save("config", dict(store.load("config"), floorplan_daily_cost=None))
aged2 = core.aged_board()
row2 = next(r for r in aged2 if r["unit"] == "un_aged")
ok("interest_note" in row2 and "not invented" in row2["interest_note"],
   "no recorded rate → dollars unknowable, not invented")
store.save("config", dict(store.load("config"), floorplan_daily_cost=9.5))

print("== lead copy + ladder ==")
out = agents.handle_message("ld_demo_lead")
body = out["steps"][0]["draft"]
ok("available as of this minute" in body and "rather than let you drive over" in body,
   "the lead reply is fast and honest about selling first")
ok("yourco" not in body.lower(), "white-label")
l9 = {"id": "ld_x", "from": "Dana", "text": "is it available", "label": "lead",
      "at": iso(now() - timedelta(hours=30)),
      "touches": [{"at": iso(now() - timedelta(hours=25))}]}
store.upsert("leads", l9)
ok(core.lead_plan(l9)["action"] == "draft_touch", "past cooldown → next touch")
l9["touches"] = [{"at": iso(now() - timedelta(hours=2))}]
ok(core.lead_plan(l9)["action"] == "none", "20h cooldown holds")
l9["touches"] = [{"at": iso(now() - timedelta(hours=90 - i * 24))} for i in range(3)]
ok("a salesperson calls" in core.lead_plan(l9)["why"], "past the ladder, a call")
b3 = agents._lead_copy(l9, 3)
ok("what you're actually\nhunting for" in b3 or "actually" in b3, "touch 3 pivots to the hunt")

print("== matrix ==")
for a in ("assert_condition_beyond_record", "quote_payment_without_terms",
          "deliver_without_title_status", "guess_trade_value"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("guess_trade_value", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no lead missed")
ok("SOMEWHERE ELSE" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("aged_interest" in r["recorded"], "floorplan interest recorded")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Floorplan interest on aged units"]["kind"] == "cash_timing",
   "floorplan is cash timing")
ok(labels["The compliance file"]["kind"] == "scenario", "compliance is a scenario")

print("== recovered, counted ==")
base = core.recovered_this_week()
u9 = store.by_id("units", "un_001")
u9["sold_at"] = iso(now() - timedelta(days=1))
store.upsert("units", u9)
d9 = store.by_id("deals", "dl_demo_titled")
d9["delivered_at"] = iso(now())
store.upsert("deals", d9)
rec = core.recovered_this_week()
ok(rec["units_sold"] == base["units_sold"] + 1, "sold units counted")
ok(rec["deals_delivered"] == base["deals_delivered"] + 1, "deliveries counted")
ok(rec["leads_answered_in_hour"] >= 1, "in-hour answers counted from timestamps")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
