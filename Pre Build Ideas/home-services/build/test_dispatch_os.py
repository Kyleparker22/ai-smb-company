#!/usr/bin/env python3
"""Dispatch OS — the honesty suite.

Every assertion here pins a REFUSAL, not a feature: the things the build must
decline to do or decline to claim. A build that passes its feature tests and
fails these is the kind of tool that loses a technical owner in one meeting.

  python3 test_dispatch_os.py
"""
import sys, tempfile
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# isolate: never touch the demo store
import os
os.environ["DISPATCHOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="dispatchos_test_")

import agents, core, seed              # noqa: E402
from core import gate, store           # noqa: E402
from _kit.store import iso, now, parse  # noqa: E402

P = F = 0


def ok(cond, label):
    global P, F
    if cond:
        P += 1
    else:
        F += 1
        print(f"  FAIL: {label}")


def section(t):
    print(f"\n{t}")


# ---------------------------------------------------------------- the emergency stop
section("the emergency stop — the one classifier biased on purpose")

for phrase in ["I smell gas in the basement", "burning smell from the vents",
               "my CO detector is going off", "water is pouring out everywhere",
               "the outlet sparked", "sewage is backing up", "there's smoke",
               "not sure, something smells weird", "no heat and we have a newborn"]:
    c = core.classify(phrase)
    ok(c["emergency"] and c["urgency"] == "emergency", f"'{phrase}' must be an emergency")

ok(core.classify("")["emergency"], "an empty report routes to a human — never assumed safe")
ok(core.classify(None)["emergency"], "an unreadable report routes to a human")
ok(core.emergency_signal("i think i smell gas")[0], "hedged wording still fires")

r = core.eval_intake()
ok(r["costly_missed"] == 0, "the eval set records zero missed emergencies")
ok(r["costly_recall"] == 1.0, "emergency recall is reported, and is 1.0 on the set")
ok("costly_note" in r, "the costly error class is named, not buried in an accuracy number")

# ---------------------------------------------------------------- refusing to guess
section("refusing to guess")

c = core.classify("the thing on the wall is beeping and I don't know what it is")
ok(c["job_class"] is None and not c["emergency"] is None, "an unmatched symptom yields no job class")
ok("clarifying question" in c["why"], "the reason says it will ask rather than book a guess")

# ---------------------------------------------------------------- capacity honesty
section("capacity — a slot offered is a slot the board can honour")

slots = [{"id": "s1", "tech_name": "T", "skills": ["hvac"], "starts_at": iso(now()),
          "from_zone": "north", "minutes_free": 180}]
ok(core.open_slots(slots, "hvac_replacement", "south") == [],
   "a 480-minute job is never offered a 180-minute slot")
ok(core.open_slots(slots, "plumb_leak", "north") == [],
   "a plumbing job is never offered an hvac-only tech")
ok(core.open_slots([dict(slots[0], minutes_free=95)], "hvac_no_cool", "south") == [],
   "a 90-minute job is refused when the drive time makes it not fit")
ok(core.open_slots(slots, "hvac_maintenance", "north"), "a job that genuinely fits IS offered")
ok(core.open_slots(slots, "nonsense_class", "north") == [], "an unknown job class yields nothing")

# ---------------------------------------------------------------- the estimate state machine
section("no estimate rests in 'presented'")

old = {"id": "e_old", "customer_name": "X Y", "scope": "s", "amount": 100.0,
       "presented_at": iso(now() - timedelta(days=core.ESTIMATE_TTL_DAYS + 2)), "state": "presented"}
ok(core.estimate_state(old) == "expired", "past TTL is expired whatever the record says")
ok(core.due_touches(old) == [], "an expired estimate gets no more touches")

mid = dict(old, id="e_mid", presented_at=iso(now() - timedelta(days=8)))
due = core.due_touches(mid)
ok([t["day"] for t in due] == [1, 3, 7], "day 1/3/7 are due at day 8, day 14 is not")
mid["touches"] = [{"day": 1}, {"day": 3}]
ok([t["day"] for t in core.due_touches(mid)] == [7], "a sent touch is never re-sent")
ok(len(core.LADDER) == 5 and core.LADDER[-1]["kind"] == "last",
   "the ladder is bounded and its last step says it is the last")
ok(set(core.LOSS_REASONS) and "price" in core.LOSS_REASONS,
   "a loss must carry a structured reason")

# ---------------------------------------------------------------- the money floor
section("the money floor — R1 on anything a homeowner could hold us to")

ok(core.MATRIX.rung_for("quote_price")["rung"] == "R1", "quoting a price is gated")
ok(core.MATRIX.rung_for("book_after_hours")["rung"] == "R1", "the after-hours premium is gated")
ok("quote_price" in core.MATRIX.never_promote(), "quoting never climbs a rung")
ok("book_after_hours" in core.MATRIX.never_promote(), "the premium never climbs a rung")
ok("propose_board" in core.MATRIX.never_promote(), "dispatch proposes forever — it never climbs")
ok(core.MATRIX.rung_for("route_emergency")["rung"] == "R3",
   "routing an emergency to a human is the safe direction, so it is autonomous")
ok(core.MATRIX.promotable("quote_price", streak=999)["promote"] is False,
   "a perfect streak cannot promote a never-promote action")
ok(core.MATRIX.promotable("draft_estimate_touch", streak=25, calibration_ok=False)["promote"] is False,
   "a clean streak without calibration evidence is not enough — it cannot tell reliable from lucky")
ok(core.MATRIX.rung_for("unknown_action_nobody_declared")["rung"] == "R1",
   "an undeclared action defaults to the approval gate")

# ---------------------------------------------------------------- the deferred ledger
section("the deferred-work ledger")

p = core.parse_note("cap reading low, out of spec. told cust, declined for now")
ok(p["recommendations"] and p["recommendations"][0]["component"] == "capacitor", "a real note parses")
p2 = core.parse_note("cust asked about a mini split for the garage, said he'd call back")
ok(p2["recommendations"] == [] and p2["unparsed"], "a note that parses to nothing is surfaced, not dropped")

rec = {"component": "capacitor", "state": "declined", "declined_at": iso(now() - timedelta(days=10))}
ok(core.reoffer_due(rec, now().replace(month=5))[0] is False, "inside the cooling-off, no re-offer")
old_rec = {"component": "capacitor", "state": "declined",
           "declined_at": iso(now() - timedelta(days=300))}
in_season = core.reoffer_due(old_rec, now().replace(month=5))
out_season = core.reoffer_due(old_rec, now().replace(month=11))
ok(in_season[0] is True, "in season and past cooling-off, it is due")
ok(out_season[0] is False and "out of season" in out_season[1], "out of season it waits, with a reason")
safety = {"component": "heat_exchanger", "state": "declined",
          "declined_at": iso(now() - timedelta(days=300))}
ok(core.reoffer_due(safety, now().replace(month=7))[0] is True,
   "a safety item re-offers out of season on purpose")
sold = {"component": "capacitor", "state": "sold", "declined_at": iso(now() - timedelta(days=300))}
ok(core.reoffer_due(sold, now().replace(month=5))[0] is False, "work already sold is never re-offered")

# ---------------------------------------------------------------- the refusal to state a number
section("numbers that cannot be computed are blank, never zero")

store.wipe()
ok(core.avg_ticket().get("_missing"), "no jobs → no average ticket, with a reason")
ok(core.undecided_value([]).get("_missing"), "no estimates → no open value, with a reason")
ok(core.automation().get("_missing"), "an empty log → no automation rate, with a reason")
ok(core.recovered_this_week().get("_missing"), "no wins → nothing claimed as recovered")

r = core.roi({})
blank_lines = [l for l in r["lines"] if l["value"] is None]
ok(len(blank_lines) == len(r["lines"]), "with no inputs at all, every ROI line is blank")
ok(all(l.get("_missing") for l in blank_lines), "each blank line says what it needs")

r2 = core.roi({"missed_calls_wk": 10, "recovered_book_rate": 0.3, "avg_ticket": 500})
line = [l for l in r2["lines"] if l["label"].startswith("Missed")][0]
ok(line["value"] == 10 * 0.3 * 500 * 52, "a line with its inputs computes, and shows its arithmetic")
ok(r2["totals"]["time_saved"]["total"] is None,
   "a subtotal with no computable line is blank, not 0")
ok("MODEL" in r2["label"], "the panel labels itself a model")

# ---------------------------------------------------------------- the seeded world
section("the seeded shop, end to end")

st = seed.build(400, 12, reset=True)
ok(st["jobs"] == 400 and st["calls"] > 400, "the seed builds a whole shop")

before = len(store.load("events"))
res = agents.run_all()
after = len(store.load("events"))
ok(after > before, "the sweeps write to the append-only log")

evs = store.load("events")
ok(all(not (e["actor"].startswith("agent:") and e.get("rung") in (None, "")) for e in evs),
   "no agent action is ever logged without a rung")
ok(all(e.get("id") and e.get("at") for e in evs), "every event is stamped and identified")

# append-only: a second sweep may add but never rewrite
ids_before = [e["id"] for e in store.load("events")]
agents.estimate_recovery()
ids_after = [e["id"] for e in store.load("events")]
ok(ids_after[:len(ids_before)] == ids_before, "the event log is append-only — earlier rows are untouched")

# emergency call in the demo set is routed, never booked
demo_emerg = [c for c in store.load("calls") if c.get("demo_tag") == "emergency"]
ok(demo_emerg, "the seed includes an emergency call")
out = agents.front_desk(demo_emerg[0]["id"])
ok(out["classification"]["emergency"] and out["steps"][0]["action"] == "route_emergency",
   "the emergency call routes to a human")
ok(not any(s["action"].startswith("book") for s in out["steps"]),
   "an emergency call is never booked into a slot by an agent")
call_after = store.by_id("calls", demo_emerg[0]["id"])
ok(call_after.get("booked_job") is None, "and no job is created from it")

# after-hours booking is queued, not executed
pend = gate.pending()
ok(isinstance(pend, list), "the approval queue exists")
q = [a for a in pend if a["action"] in ("draft_estimate_touch", "book_after_hours")]
ok(q, "gated actions land in the queue rather than executing")
ok(all(a["state"] == "pending" for a in q), "and they sit there until a human decides")

# nothing outward moved without a human
sent = [e for e in store.load("events") if e["kind"] == "estimate_touch_sent"]
ok(all(e["actor"].startswith("human:") for e in sent),
   "every touch that was SENT carries a human actor — no agent sent anything")

# the demo estimate is the flagship
est = store.by_id("estimates", "est_demo_1")
ok(est and est["amount"] == 9400.0, "the $9,400 demo estimate exists")
ok(len(est.get("touches", [])) >= 3, "and by day 16 it has drafted its due touches")
ok(all(t.get("sent_at") is None for t in est["touches"]),
   "none of which were sent — they are waiting on a human")

section("R0 is not a slow yes — it never becomes an approvable row")
_before = len(gate.pending())
_r = gate.act("propose_board", "dispatch", "r0_probe", {"summary": "probe"})
ok(_r.get("refused") is True and _r.get("executed") is False,
   "an R0 action returns a refusal, not a queued approval")
ok(len(gate.pending()) == _before,
   "and it adds nothing to the approval queue — a human must not be offered a button "
   "that clicks past a prohibition")
ok(any(e["kind"] == "refused" and (e.get("detail") or {}).get("action") == "propose_board"
       for e in store.load("events")),
   "the refusal is recorded in the append-only log")

print(f"\n{P} passed, {F} failed")
sys.exit(1 if F else 0)
