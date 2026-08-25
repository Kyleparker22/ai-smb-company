#!/usr/bin/env python3
"""Bay OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["BAYOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="bayos-test-")
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


# ---------------------------------------------------------------- classifier + eval
ok(core.classify_item("front brake pads 2mm, rotors scored")["label"] == "safety_critical",
   "worn brakes are safety-critical")
ok(core.classify_item("cabin air filter dirty")["label"] == "cosmetic", "cabin filter is cosmetic")
ok(core.classify_item("coolant service due by mileage")["label"] == "deferrable",
   "fluid service is deferrable")
ok(core.classify_item("")["label"] == "needs_review", "an empty finding routes to a human")
ok(core.classify_item("customer states noise sometimes")["label"] == "needs_review",
   "vague findings are never guessed")

ev = core.run_eval()
ok(ev["costly_label"] == "safety_critical", "the costly class is the safety miss")
ok(ev["costly_missed"] == 0, f"zero safety items missed in the shipped eval ({ev['costly_missed']})")
ok("ENDS A SHOP" in ev["costly_note"], "the eval names the stake")

# ---------------------------------------------------------------- the safety-text refusal
store.wipe()
store.save("config", {"company": "t"})
store.save("declined", [
    {"id": "d_safe", "text": "front brake pads 2mm", "value": 780,
     "label": "safety_critical", "declined_at": iso(now() - timedelta(days=60))},
    {"id": "d_def", "text": "coolant service due", "value": 190,
     "label": "deferrable", "declined_at": iso(now() - timedelta(days=60))},
])
r = agents.send_text("d_safe")
ok("refused" in r, "a safety item cannot be texted")
ok("never a marketing text" in r["refused"], "…and the refusal states the rule")
ok(not any(a for a in store.load("approvals")), "the refusal never became an approvable row")
ok(any(e["kind"] == "refused" for e in store.events(subject="d_safe")), "the refusal is logged")

r = agents.send_text("d_def")
ok(r.get("approval"), "a deferrable item text queues for a human — R1, not auto-sent")

# ---------------------------------------------------------------- the re-offer plan
plan = core.reoffer_plan({"label": "safety_critical", "declined_at": iso(now() - timedelta(days=90))})
ok(plan["action"] == "call_task", "a safety item becomes a call task, never a drip")
plan = core.reoffer_plan({"label": "deferrable", "declined_at": iso(now() - timedelta(days=10))})
ok(plan["action"] == "none" and "cooldown" in plan["why"], "cooldown is respected")
plan = core.reoffer_plan({"label": "deferrable", "declined_at": iso(now() - timedelta(days=90)),
                          "touches": [{"at": iso()}] * core.MAX_TOUCHES})
ok(plan["action"] == "none" and "silence is an answer" in plan["why"], "the ladder is bounded")
plan = core.reoffer_plan({"label": "deferrable", "demo_tag": "demo",
                          "declined_at": iso(now() - timedelta(days=90))})
ok(plan["action"] == "none", "demo rows are never swept")

# ---------------------------------------------------------------- intake
ok(core.classify_call("my brakes are to the floor")["label"] == "safety_priority",
   "an unsafe vehicle is priority")
c = core.classify_call("what's wrong with my car? is it the alternator")
ok(c["label"] == "no_phone_diagnosis", "phone diagnosis is refused")
ok("never guess" in c["why"], "…with the reason stated")
ok(core.classify_call("can I book an oil change thursday")["label"] == "booking", "booking routes")
ok(core.classify_call("")["label"] == "human", "empty transcript goes to a person")

# ---------------------------------------------------------------- price bands
store.save("ros", [{"id": f"r{i}", "kind": "brake_job", "total": 400 + i * 50,
                    "closed_at": iso()} for i in range(8)])
b = core.price_band("brake_job")
ok(b.get("band") and b["band"][0] < b["band"][1], "a band computes from own ROs")
ok("inspection" in b["basis"], "the band says a firm price needs an inspection")
b = core.price_band("timing_service")
ok(b.get("_missing") and "need 6" in b["_missing"], "below 6 ROs the band refuses")

# ---------------------------------------------------------------- comebacks
store.save("ros", [])
cb = core.comeback_rate()
ok(cb.get("_missing") and "need 50" in cb["_missing"], "the comeback rate refuses below its floor")
rows = []
base = now() - timedelta(days=100)
for i in range(60):
    rows.append({"id": f"r{i}", "vehicle_id": f"v{i%40}", "system": "engine",
                 "total": 500, "closed_at": iso(base + timedelta(days=i))})
rows.append({"id": "rA", "vehicle_id": "vX", "system": "brakes", "total": 500,
             "closed_at": iso(base + timedelta(days=10))})
rows.append({"id": "rB", "vehicle_id": "vX", "system": "brakes", "total": 500,
             "closed_at": iso(base + timedelta(days=20))})
store.save("ros", rows)
cb = core.comeback_rate()
ok(cb.get("comebacks", 0) >= 1 and any(r["ro"] == "rB" for r in cb["rows"]),
   "a same-vehicle same-system repeat inside 30 days is counted")

# ---------------------------------------------------------------- R0 probes
for action in ("state_vehicle_safe", "send_safety_text", "phone_diagnosis"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("state_vehicle_safe", "send_safety_text", "phone_diagnosis")
           for a in core.gate.pending()), "no R0 action reached the approval queue")
ok("quote_firm_price" in core.matrix.never_promote(), "a firm price can never promote")

# ---------------------------------------------------------------- sweeps
store.save("declined", [
    {"id": "s1", "text": "front brake pads 2mm, caliper sticking", "value": 780,
     "declined_at": iso(now() - timedelta(days=60))},
    {"id": "s2", "text": "engine air filter at 70%", "value": 45,
     "declined_at": iso(now() - timedelta(days=60))},
])
store.save("approvals", [])
out = agents.classify_sweep()
ok(out["classified"] == 2 and out["safety_calls"] == 1,
   "the sweep classifies and raises exactly one safety call task")
out = agents.reoffer_sweep()
ok(out["drafted"] == 1, "only the non-safety item is drafted for re-offer")
d = store.by_id("declined", "s1")
ok(d["label"] == "safety_critical" and not (d.get("touches")),
   "the safety item never entered the ladder")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Declined work re-offered and won"]["value"] is None,
   "the revenue line is blank without the operator's close rate — never invented")
ok(labels["Comeback exposure made visible"]["kind"] == "scenario",
   "comeback exposure is a scenario, never a saving")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- drafted copy
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

store.save("customers", [{"id": "c9", "name": "Dana Whitfield"}])
d9 = {"id": "d9", "customer_id": "c9", "text": "engine air filter at 70%", "value": 89,
      "label": "deferrable", "declined_at": _iso(_now() - timedelta(days=50))}
store.upsert("declined", d9)
body = agents._reoffer_copy(d9, 1)
ok("Dana" in body and "$89" in body and "engine air filter" in body,
   "touch-1 copy carries name, value, and the sheet's own words")
ok("yourco" not in body.lower(), "white-label: no yourco name in outward copy")
body3 = agents._reoffer_copy(d9, 3)
ok("last note" in body3 and "no problem" in body3,
   "touch 3 closes the ladder without pressure — silence is an answer")
for b in (body, body3):
    ok(not any(w in b.lower() for w in ("unsafe", "danger", "risk your")),
       "re-offer copy never makes a safety claim either way")

out = agents.reoffer_sweep()
d9 = store.by_id("declined", "d9")
ok(d9.get("touches") and d9["touches"][0].get("body"), "the drafted body is recorded on the touch")

# ---------------------------------------------------------------- the price flow
store.save("ros", [])
r = agents.price_quote("front_brakes")
ok(r["band"] is None and "eyes on the car" in r["say"],
   "no history → the band refuses and the copy says why")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "quote_firm_price"
       for e in store.events()), "every price answer logs the firm-price refusal")
store.save("ros", [{"id": f"r{i}", "kind": "front_brakes", "total": 400 + 20 * i,
                    "closed_at": _iso(_now() - timedelta(days=i + 1))} for i in range(8)])
r = agents.price_quote("front_brakes")
ok(r["band"] and r["band"][0] <= r["band"][1], "with history the band states its middle half")
ok("our own recent work" in r["say"] and "inspection" in r["say"],
   "the spoken answer names its basis and the inspection rule")
ok("$" in r["say"] and "firm number" in r["say"], "a band, never a firm number")

# ---------------------------------------------------------------- recovered, counted
rec = core.recovered_this_week()
ok(rec["items_won"] == 0 and rec["value_won"] == 0, "nothing recovered → zero, honestly")
d9["recovered_at"] = _iso(_now() - timedelta(days=2))
store.upsert("declined", d9)
store.log_event("reoffer_sent", "d9", "human:advisor", "R1", {})
rec = core.recovered_this_week()
ok(rec["items_won"] == 1 and rec["value_won"] == 89, "a recovered item is counted with its sheet value")
ok(rec["reoffers_sent"] == 1, "sends are counted from the event log")
ok("counted" in rec["note"], "recovered names its basis")

# stale recoveries fall out of the 7-day window
d9["recovered_at"] = _iso(_now() - timedelta(days=12))
store.upsert("declined", d9)
ok(core.recovered_this_week()["items_won"] == 0, "an old recovery is not this week's number")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
