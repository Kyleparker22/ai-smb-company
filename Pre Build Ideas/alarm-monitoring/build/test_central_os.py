#!/usr/bin/env python3
"""Central OS — the suite. `python3 test_central_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["CENTRALOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="centralos_test_")
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
ok(len(store.load("accounts")) >= 200, "accounts seeded")

print("== triage: the SE reads come first ==")
for text, want in (("put my account in test mode for the afternoon", "test_mode_request"),
                   ("disable the motion sensors this weekend, we have guests", "test_mode_request"),
                   ("pause monitoring while we renovate the kitchen", "test_mode_request"),
                   ("going to trip the alarm moving furniture, just ignore it", "test_mode_request"),
                   ("my passcode is 4471, go ahead and cancel that", "passcode_in_text"),
                   ("the safe word is bluebird, disregard the signal", "passcode_in_text"),
                   ("smoke alarm activation at the warehouse on 5th", "fire_signal"),
                   ("co detector signal at the riverside house", "fire_signal"),
                   ("motion signal tripped in zone 4 at the office", "burglary_signal"),
                   ("glass break signal at the storefront", "burglary_signal"),
                   ("question about my bill this month", "billing"),
                   ("", "human"),
                   ("what time does the office open", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

print("== the test-mode refusal ==")
out = agents.handle_message("ms_demo_test")
step = out["steps"][0]
ok("no account state changes from this thread" in step["refused"], "refused flat")
ev = next(e for e in store.events()
          if e["kind"] == "refused"
          and (e["detail"] or {}).get("action") == "enter_test_mode_from_message")
ok(ev["detail"]["verbatim"] == "put my account in test mode for the afternoon"
   and ev["detail"]["from"] == "unknown number",
   "the request and sender are preserved verbatim")
ok(any(e["kind"] == "open_callback_task" for e in store.events()),
   "the verified-callback task opens at R2")
body = step["draft"]
ok("that includes you, and that's the point" in body,
   "the copy explains the rule without apology")
ok("yourco" not in body.lower(), "white-label")

print("== the passcode refusal ==")
out = agents.handle_message("ms_demo_pass")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "accept_passcode_in_text"
       for e in store.events()), "accept_passcode_in_text logged")
body = out["steps"][0]["draft"]
ok("we don't read them" in body and "red flag" in body,
   "the copy teaches the rule — and warns about companies that don't hold it")

print("== the fire rule ==")
r = agents.cancel_dispatch("sg_demo_fire", human="operator-7", verified_callback=True)
ok("refused" in r and "never cancelled by this system" in r["refused"],
   "fire dispatch cannot be cancelled — even by a human with a callback")
ok("burnt toast" in r["refused"], "the refusal explains the asymmetry")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "cancel_fire_dispatch"
       for e in store.events()), "cancel_fire_dispatch logged")

print("== the burglary cancel path ==")
r = agents.cancel_dispatch("sg_demo_burg")
ok("refused" in r and "human decision" in r["refused"], "software holds no cancel authority")
r = agents.cancel_dispatch("sg_demo_burg", human="operator-7")
ok("refused" in r and "verified callback" in r["refused"], "no callback, no cancel")
r = agents.cancel_dispatch("sg_demo_burg", human="operator-7", verified_callback=True)
ok(r.get("cancelled") and "both recorded" in r["why"],
   "a human with a verified callback may cancel — both facts recorded")

print("== permits & fines ==")
ps = core.permit_state({"city": "Riverton", "permit_expires": iso(now() - timedelta(days=5))})
ok(ps["state"] == "expired" and "DATE ALERT" in ps["label"], "expired permit is a date alert")
ps = core.permit_state({"city": "Riverton"})
ok(ps["state"] == "unregistered" and "fines" in ps["why"], "no permit reads unregistered")
ok("_missing" in core.permit_state({"city": "Nowhere"}), "an unknown city refuses, never guesses")
fe = core.fine_exposure({"city": "Lakewood", "false_alarms_ytd": 4})
ok(fe["accrued"] == 0 + 25 + 75 + 150 and fe["next_costs"] == 300,
   "fines accrue against the city's recorded schedule")
out = agents.permit_sweep()
ok(out["alerts"] >= 1 and out["renewal_drafts"] >= 1, "lapses raise alerts and renewal drafts")

print("== matrix ==")
for a in ("enter_test_mode_from_message", "accept_passcode_in_text", "cancel_fire_dispatch",
          "cancel_burglary_dispatch"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("cancel_fire_dispatch", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no test-mode request missed")
ok("burglar" in ev["costly_note"].lower(), "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("fine_exposure" in r["recorded"] and "lapses" in r["recorded"], "exposure counted")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["False-alarm fine exposure surfaced"]["kind"] == "scenario",
   "prevented fines are never counted")

print("== recovered, counted ==")
rec = core.recovered_this_week()
ok(rec["social_engineering_refused"] >= 2, "SE refusals counted from the log")
agents.verify_callback("ac_002", "operator-7")
rec = core.recovered_this_week()
ok(rec["callbacks_verified"] == 1, "verified callbacks counted")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
