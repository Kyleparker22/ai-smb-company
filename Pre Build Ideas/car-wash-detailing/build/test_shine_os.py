#!/usr/bin/env python3
"""Shine OS — the suite. `python3 test_shine_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["SHINEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="shineos_test_")
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
ok(len(store.load("members")) >= 400, "members seeded")

print("== triage: damage first ==")
for text, want in (("your wash snapped my antenna clean off", "damage_claim"),
                   ("there are swirl scratches all over the hood since the tunnel", "damage_claim"),
                   ("the machine bent my wiper arm", "damage_claim"),
                   ("cancel my membership please, we moved across town", "cancellation"),
                   ("stop charging my card, I sold the car", "cancellation"),
                   ("I was charged twice this month", "billing"),
                   ("wrong amount on my receipt from tuesday", "billing"),
                   ("can I book a full detail for saturday", "detail"),
                   ("is the interior detail available sunday", "detail"),
                   ("", "human"),
                   ("you guys did a great job on the truck", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:42]} → {want}")

print("== the claim protocol ==")
out = agents.handle_message("ms_demo_damage")
step = out["steps"][0]
ok(step["action"] == "log_damage_claim", "claim logged verbatim")
ok("footage" in step["said"].lower() and "nothing is denied" in step["said"].lower(),
   "the protocol pulls footage and denies nothing")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "deny_damage_claim"
       for e in store.events()), "deny_damage_claim refused + logged")
ok(any(e["kind"] == "pull_footage_task" for e in store.events()),
   "the footage task executes at R2 and lands in the log")
ok(len(store.load("claims")) == 1, "a claim row was created")

print("== the cancellation clock ==")
out = agents.handle_message("ms_demo_cancel")
ok(out["steps"][0]["action"] == "start_cancel_clock", "the clock starts at the request")
mb = store.by_id("members", "mb_000")
ok(mb.get("cancel_requested_at"), "the request is recorded on the member")
okc, why = core.can_charge(mb)
ok(not okc and "cannot be expressed" in why, "a charge after the request is refused")
r = agents.charge_member("mb_000", 29)
ok("refused" in r, "the charge path refuses")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "charge_after_cancel_request"
       for e in store.events()), "charge_after_cancel_request logged")
save = agents._save_copy(mb)
ok("processing as asked" in save and "no hard feelings" in save,
   "the save offer says the cancel proceeds regardless")

print("== dunning ==")
m9 = {"id": "mb_x", "name": "Jordan Osei", "dues": 29}
store.upsert("members", m9)
store.upsert("payments", {"id": "py_x", "member_id": "mb_x", "amount": 29, "failed": True})
p1 = core.dunning_plan(m9)
ok(p1["touch"] == 1 and "didn't go through" in p1["text"], "touch 1 is friendly")
m9["dunning_touches"] = [{"at": iso(now() - timedelta(days=6))}]
p2 = core.dunning_plan(m9)
ok(p2["touch"] == 2 and "pauses" in p2["text"], "touch 2 states the consequence plainly")
m9["dunning_touches"].append({"at": iso(now() - timedelta(days=6))})
p3 = core.dunning_plan(m9)
ok(p3["touch"] == 3 and "CANCEL" in p3["text"] and "same-day" in p3["text"],
   "touch 3 offers the honest exit")
for p in (p1, p2, p3):
    ok(core.dunning_text_ok(p["text"])[0], f"touch {p['touch']} passes the threat check")
ok(not core.dunning_text_ok("pay or we send this to collections")[0],
   "threat language is structurally refused")
ok("yourco" not in (p1["text"] + p2["text"] + p3["text"] + save).lower(), "white-label")

print("== weather copy ==")
w = agents._weather_copy({"customer": "Dana", "kind": "ceramic coating"})
ok("isn't worth your money" in w and "reply 1 or 2" in w,
   "the weather reschedule is honest and concrete")

print("== matrix ==")
for a in ("deny_damage_claim", "delay_cancellation", "charge_after_cancel_request",
          "threaten_in_dunning"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("deny_damage_claim", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a_["action"] == "deny_damage_claim" and a_["state"] == "pending"
           for a_ in store.load("approvals")), "R0 never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no damage claim missed")
ok("ONE-STAR" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("open_failures" in r["recorded"], "open failures recorded")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["The claims file"]["kind"] == "scenario", "the claims file is a scenario")

print("== recovered, counted ==")
base = core.recovered_this_week()
store.upsert("payments", {"id": "py_y", "member_id": "mb_x", "amount": 29, "failed": True,
                          "recovered_at": iso(now() - timedelta(days=1))})
c9 = store.load("claims")[0]
c9["resolved_at"] = iso(now())
store.upsert("claims", c9)
rec = core.recovered_this_week()
ok(rec["payments_recovered"] == base["payments_recovered"] + 1
   and rec["recovered_value"] >= 29, "a recovered payment is counted")
ok(rec["claims_resolved"] == base["claims_resolved"] + 1, "human-resolved claims counted")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
