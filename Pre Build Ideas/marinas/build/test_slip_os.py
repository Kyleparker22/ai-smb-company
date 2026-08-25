#!/usr/bin/env python3
"""Slip OS — the suite. `python3 test_slip_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["SLIPOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="slipos_test_")
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
ok(len(store.load("slips")) >= 240, "slips seeded")

print("== triage: spill first ==")
for text, want in (("there's diesel in the water by the fuel dock", "spill"),
                   ("seeing a sheen around slip 40 this morning", "spill"),
                   ("oil is leaking into the water from the trawler", "spill"),
                   ("is there a sheen by the transient dock or is that just pollen", "spill"),
                   ("need the boat hauled and bottom paint before june", "work_request"),
                   ("can you winterize the engine this month", "work_request"),
                   ("shrink wrap the boat when you haul it", "work_request"),
                   ("any slip open for a 32 footer this season", "waitlist"),
                   ("how do I get on the list for dock space", "waitlist"),
                   ("question about my storage fee this quarter", "billing"),
                   ("", "human"),
                   ("the launch ramp gate code isn't working", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

print("== the spill protocol ==")
out = agents.handle_message("ms_demo_spill")
step = out["steps"][0]
ok("USCG exhibit" in step["said"], "the protocol names the stake")
ok("asserted or denied" in step["said"], "cause is neither asserted nor denied")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "assert_spill_cause"
       for e in store.events()), "assert_spill_cause refused + logged")
ev = next(e for e in store.events() if e["kind"] == "escalate_spill")
ok(ev["detail"]["verbatim"] == "there's diesel in the water by the fuel dock",
   "the report travels verbatim")

print("== the authorization gate ==")
r = agents.start_work("wo_demo_verbal")
ok("refused" in r and "a note, not a gate pass" in r["refused"], "verbal only → no clock-in")
ok("he said go\nahead at the fuel dock" in r["refused"] or "fuel dock" in r["refused"],
   "the refusal names the failure mode")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "start_work_unauthorized"
       for e in store.events()), "start_work_unauthorized logged")
ok(not store.by_id("workorders", "wo_demo_verbal").get("started_at"), "the clock did not start")
r = agents.start_work("wo_demo_verbal", by="Renner (owner)",
                      scope="haul, pressure wash, bottom paint", rate_basis="posted yard rates")
ok(r.get("started") and "Renner (owner)" in r["why"], "the recorded authorization starts it")

print("== the storage clamp ==")
sb = core.storage_bill(store.by_id("vessels", "vs_demo_splashed"))
ok(sb["days"] in (30, 31) and "recorded departure" in sb["ends_at"],
   "the meter stopped at the splash — 10 days ago, not today")
ok(sb["total"] == sb["days"] * 24, "the arithmetic is the rate × the stamped days")
ok("_missing" in core.storage_bill({}), "no arrival → nothing billed")
ok("_missing" in core.storage_bill({"arrived_at": iso(now())}), "no rate → nothing priced")

print("== the waitlist arithmetic ==")
slip = store.by_id("slips", "sl_demo_open")
fit = core.slip_fit(slip, store.by_id("waitlist", "wl_demo_fits"))
ok(fit["fit"] is True, "the 30ft boat fits the 34ft slip")
fit = core.slip_fit(slip, store.by_id("waitlist", "wl_demo_toobig"))
ok(fit["fit"] is False and "length 44ft > slip max 34ft" in fit["why"],
   "the 44ft boat is blocked with the arithmetic shown")
fit = core.slip_fit(slip, {"length_ft": 30, "beam_ft": None, "draft_ft": 4})
ok(fit["fit"] is None and "unknowable, not assumed" in fit["why"],
   "missing dimensions read unknowable")
ranked = agents.offer_slip("sl_demo_open")
ok(any(b["name"] == "Ray Havel" for b in ranked["blocked"]), "the too-big boat is blocked")
ok(len(ranked["candidates"]) >= 1, "fit candidates ranked in recorded order")

print("== drafted copy ==")
au = agents._auth_request_copy({"from": "Pruitt"})
ok("one click" in au and "boring" in au, "the auth copy sells the discipline")
wl = agents._waitlist_copy({"from": "Osei"})
ok("arithmetic, not the vibes" in wl and "48 hours" in wl, "the waitlist copy states the system")
ok("yourco" not in (au + wl).lower(), "white-label")

print("== matrix ==")
for a in ("assert_spill_cause", "start_work_unauthorized", "assert_seaworthiness",
          "bill_past_departure"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("assert_seaworthiness", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no spill missed")
ok("USCG" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("open_slips" in r["recorded"], "open slips counted")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["The spill log"]["kind"] == "scenario", "the spill log is never a saving")

print("== recovered, counted ==")
rec = core.recovered_this_week()
ok(rec["workorders_started"] >= 1, "started work orders counted")
ok(rec["spills_escalated"] >= 1, "spill escalations counted")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
