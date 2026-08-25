#!/usr/bin/env python3
"""Yard OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["YARDOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="yardos-test-")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import agents, core
from core import store
from _kit.store import iso, now, parse

PASS = FAIL = 0


def ok(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL  {msg}")


# ---------------------------------------------------------------- the billing clamp
r = {"id": "r1", "on_rent_at": iso(now() - timedelta(days=10)),
     "off_rent_called_at": iso(now() - timedelta(days=4)), "day_rate": 100.0}
bd = core.billable_days(r)
ok(bd["days"] == 6, f"billable days stop at the recorded call (got {bd['days']})")
ok("off-rent call" in bd["ends_at"], "the end of billing names the call")

inv = core.invoice_preview(r, through=iso(now() + timedelta(days=7)))
ok(inv["days"] == 6, "billing through NEXT WEEK still clamps to the call")
ok("do not exist" in inv.get("clamped", ""), "…and the clamp is named on the invoice")
ok(inv["amount"] == 600.0, "the amount is days × rate, nothing more")

still_on = {"id": "r2", "on_rent_at": iso(now() - timedelta(days=3)), "day_rate": 100.0}
ok(core.billable_days(still_on)["days"] in (3, 4), "a live rental bills to today")
ok(core.billable_days({"id": "r3"}).get("_missing"), "no on-rent date → nothing can be billed")
ok(core.invoice_preview({"id": "r4", "on_rent_at": iso(now())}).get("_missing"),
   "no day rate → nothing can be priced")

# ---------------------------------------------------------------- damage evidence
store.wipe()
store.save("config", {"company": "t"})
store.save("conditions", [
    {"id": "c_out", "rental_id": "rv", "kind": "checkout", "photos": 5, "damage": []},
    {"id": "c_in", "rental_id": "rv", "kind": "checkin", "photos": 6, "damage": ["bent boom section"]},
    {"id": "c_in2", "rental_id": "rn", "kind": "checkin", "photos": 3, "damage": ["cracked window"]},
    {"id": "c_out3", "rental_id": "rc", "kind": "checkout", "photos": 4, "damage": ["torn seat"]},
    {"id": "c_in3", "rental_id": "rc", "kind": "checkin", "photos": 4, "damage": ["torn seat"]},
])
v = core.damage_claim("rv")
ok(v["assertable"] and v["new_damage"] == ["bent boom section"],
   "with the evidence pair, new damage is assertable")
v = core.damage_claim("rn")
ok(not v["assertable"] and "checkout condition record" in v["refused"],
   "missing checkout → cannot assert damage, missing record named")
v = core.damage_claim("rc")
ok(not v["assertable"] and "already on checkout" in v["refused"],
   "pre-existing damage is never charged")
v = core.damage_claim("rx")
ok(not v["assertable"], "no records at all → refused")

r = agents.try_damage_claim("rn")
ok("refused" in r and any(e["kind"] == "refused" for e in store.events(subject="rn")),
   "the evidence refusal is logged")
ok(not any(a for a in store.load("approvals")), "no claim draft without evidence")
r = agents.try_damage_claim("rv")
ok(r.get("gate", {}).get("approval"), "the evidenced claim drafts at R1 for a human")

# ---------------------------------------------------------------- call triage + eval
ok(core.classify_call("we're done with the mini ex, come get it")["label"] == "off_rent",
   "an off-rent call classifies")
ok(core.classify_call("the skid steer won't start")["label"] == "breakdown", "a breakdown classifies")
ok(core.classify_call("")["label"] == "human", "empty goes to a person")
ev = core.run_eval()
ok(ev["costly_label"] == "off_rent" and ev["costly_missed"] == 0,
   f"zero missed off-rent calls in the shipped eval ({ev['costly_missed']})")
ok("OVERBILLED" in ev["costly_note"], "the eval names the stake")

# handle_call records the clock at the call
store.save("rentals", [{"id": "r_live", "unit_id": "u1", "on_rent_at": iso(now() - timedelta(days=5)),
                        "day_rate": 150.0}])
store.save("calls", [{"id": "c1", "transcript": "stop the billing on the generator, we finished friday",
                      "rental_id": "r_live", "at": iso(now() - timedelta(hours=1))}])
out = agents.handle_call("c1")
rl = store.by_id("rentals", "r_live")
ok(rl.get("off_rent_called_at") == store.by_id("calls", "c1")["at"],
   "the off-rent record carries the CALL's timestamp, not processing time")
ok(any(a["action"] == "schedule_pickup" for a in store.load("approvals")),
   "the pickup queues for a human dispatcher")

# ---------------------------------------------------------------- the standing limit
store.save("approvals", [])
r = agents.waiver("r_live", 40)
ok(r["executed"] and r["rung"] == "R2", "a small waiver executes at R2 and logs")
r = agents.waiver("r_live", 400)
ok(not r["executed"] and r.get("approval"), "a waiver above the limit demotes to the gate")
ok("standing limit" in r["reason"], "…and the demotion names the limit")

# ---------------------------------------------------------------- R0 probes
for action in ("backdate_off_rent", "assert_damage_without_evidence"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("backdate_off_rent", "assert_damage_without_evidence")
           for a in core.gate.pending()), "no R0 action reached the approval queue")

# ---------------------------------------------------------------- utilization + queue
store.save("fleet", [{"id": "u1", "cls": "skid_steer"}, {"id": "u2", "cls": "skid_steer"}])
store.save("rentals", [
    {"id": "q1", "unit_id": "u1", "cls": "skid_steer", "on_rent_at": iso(now() - timedelta(days=9))},
    {"id": "q2", "unit_id": "u9", "cls": "ghost_class", "on_rent_at": iso(now() - timedelta(days=9))},
    {"id": "q3", "unit_id": "u2", "cls": "skid_steer",
     "on_rent_at": iso(now() - timedelta(days=30)),
     "off_rent_called_at": iso(now() - timedelta(days=6))},
])
util = {u["cls"]: u for u in core.utilization()}
ok(util["skid_steer"]["rate"] == 0.5, "utilization is counted: 1 of 2 on rent")
ok(util["ghost_class"]["rate"] is None and "denominator is missing" in util["ghost_class"]["_missing"],
   "a class with no fleet units refuses its rate")
q = core.pickup_queue()
ok(len(q) == 1 and q[0]["rental"] == "q3" and q[0]["days_waiting"] == 6,
   "off-rent-not-picked-up is the counted yard leak")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Pickup-queue days put back on rent"]["value"] is None,
   "the queue line is blank without the operator's re-rent share")
ok(labels["Credit memos avoided"]["kind"] == "scenario",
   "avoided disputes are a scenario, never a saving")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("job's finished with the boom lift, come grab it whenever", "off_rent"),
                   ("error code 52 on the telehandler screen", "breakdown"),
                   ("gonna need the mini ex a little longer, through the 20th", "extension")):
    ok(core.classify_call(text)["label"] == want, f"triage: {text[:40]} → {want}")

# ---------------------------------------------------------------- drafted copy
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

r9 = {"id": "rn9", "unit_id": "EX-210", "customer_id": "c1", "day_rate": 420,
      "on_rent_at": _iso(_now() - timedelta(days=9))}
store.upsert("rentals", r9)
body = agents._extension_copy(r9)
ok("EX-210" in body and "$420/day" in body, "extension copy restates unit and rate")
ok("clock stops at that call" in body, "extension copy restates the off-rent rule")
ok("yourco" not in body.lower(), "white-label: no yourco name in outward copy")

store.upsert("conditions", {"id": "cd1", "rental_id": "rn9", "kind": "checkout",
                            "photos": 14, "damage": []})
store.upsert("conditions", {"id": "cd2", "rental_id": "rn9", "kind": "checkin",
                            "photos": 11, "damage": ["cracked left window"]})
res = agents.try_damage_claim("rn9")
ok(res["assertable"] and "cracked left window" in res["draft"], "claim draft names the finding")
ok("14 photos" in res["draft"] and "11 at return" in res["draft"],
   "claim draft cites the evidence pair's photo counts")
ok(not any(w in res["draft"].lower() for w in ("negligen", "fault", "abuse")),
   "no accusation language in the claim draft")

# ---------------------------------------------------------------- the pickup chaser
store.upsert("rentals", {"id": "rn10", "unit_id": "SS-8", "customer_id": "c2", "day_rate": 300,
                         "on_rent_at": _iso(_now() - timedelta(days=20)),
                         "off_rent_called_at": _iso(_now() - timedelta(days=4))})
out = agents.pickup_sweep()
ok(out["alerts"] >= 1, "a unit waiting 4 days raises a dispatch alert")
ok(any(e["kind"] == "pickup_overdue" and e["subject"] == "rn10" for e in store.events()),
   "the alert executes at R2 and lands in the log")
out = agents.pickup_sweep()
ok(out["alerts"] == 0, "the 3-day alert cooldown holds — no re-nag")

# ---------------------------------------------------------------- recovered, counted
rec = core.recovered_this_week()
ok(rec["units_picked_up"] == 0 and rec["claims_sent"] == 0, "nothing moved → zeros, honestly")
r10 = store.by_id("rentals", "rn10")
r10["picked_up_at"] = _iso(_now() - timedelta(days=1))
store.upsert("rentals", r10)
store.log_event("draft_damage_claim", "rn9", "human:owner", "R1", {"approval": "apx"})
before = core.recovered_this_week()["waivers_issued"]
agents.waiver("rn9", 40)
rec = core.recovered_this_week()
ok(rec["units_picked_up"] == 1, "a pickup is counted from the book")
ok(rec["claims_sent"] == 1, "a human-sent claim is counted; agent drafts are not")
ok(rec["waivers_issued"] == before + 1 and rec["waiver_total"] >= 40,
   "small waivers execute at R2 and are counted with their total")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
