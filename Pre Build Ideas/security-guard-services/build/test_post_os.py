#!/usr/bin/env python3
"""Post OS — the suite. `python3 test_post_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["POSTOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="postos_test_")
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
ok(len(store.load("guards")) >= 120, "guards seeded")

print("== triage: incident first ==")
for text, want in (("two guys got into a fight at the loading dock, police came", "incident"),
                   ("someone is down in the parking structure, calling the ambulance", "incident"),
                   ("guard reported a weapon spotted in a backpack at gate 3", "incident"),
                   ("caught a trespasser in the east stairwell", "incident"),
                   ("I can't make my shift tonight, kid is sick", "callout"),
                   ("no-show at the courthouse post this morning", "callout"),
                   ("we need an extra guard for the event saturday", "coverage_request"),
                   ("can you cover the warehouse this week, our guy quit", "coverage_request"),
                   ("when does my armed card expire", "credential"),
                   ("my guard card renewal is due, what do I need", "credential"),
                   ("", "human"),
                   ("paycheck question, who do I talk to", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

print("== append-only narratives ==")
out = agents.handle_message("rp_demo_incident")
ok(out["steps"][0]["action"] == "record_incident", "incident recorded verbatim")
inc = store.load("incidents")[0]
ok(inc["narrative"] == "two guys got into a fight at the loading dock, police came",
   "the narrative is the guard's words, untouched")
r = core.correct_incident(inc["id"], "corrected: three individuals, one detained", "gd_001")
ok(r["supersedes"] == inc["id"], "a correction points at the original")
ok(store.by_id("incidents", inc["id"]), "the original remains")
r2 = core.correct_incident(inc["id"], "the client's version", "someone_else")
ok("refused" in r2 and "only the reporting guard" in r2["refused"],
   "nobody else corrects a guard's narrative")
adj = core.adjust_request(inc["id"], "Riverside PM", "soften the police part")
ok("now\nbe part" in adj["refused"] or "part of the record" in adj["refused"],
   "the adjust request is refused and preserved")
ev = next(e for e in store.events()
          if e["kind"] == "refused" and (e["detail"] or {}).get("action") == "edit_incident_narrative")
ok(ev["detail"]["verbatim"] == "soften the police part" and ev["detail"]["requester"] == "Riverside PM",
   "the request and requester are on the record verbatim")
ok(not hasattr(core, "edit_incident") and not hasattr(core, "delete_incident"),
   "no edit and no delete exist in the module")

print("== the credential gate ==")
okf, why = core.can_fill(store.by_id("posts", "ps_demo_armed"),
                         store.by_id("guards", "gd_demo_expired"))
ok(not okf and "expired: guard_card" in why, "the expired card is named")
ok("liability the\nclient is paying" in why or "liability the client is paying" in why.replace("\n", " "),
   "the refusal names the stake")
r = agents.fill_post("ps_demo_armed", "gd_demo_expired")
ok("refused" in r, "the fill refuses")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "fill_post_unqualified"
       for e in store.events()), "fill_post_unqualified logged")
r = agents.fill_post("ps_demo_armed", "gd_demo_clean")
ok(r.get("rung") == "R1" and r.get("approval"), "the clean guard queues at R1")
okf, why = core.can_fill({"required_creds": ["guard_card", "armed"]},
                         {"name": "X", "credentials": {"guard_card": iso(now() + timedelta(days=10))}})
ok(not okf and "missing: armed" in why, "a missing credential is named")

print("== coverage board is gate-built ==")
cb = core.coverage_board()
armed_post = next((p for p in cb if p["post"] == "ps_demo_armed"), None)
if armed_post:
    ok(all("gd_demo_expired" != c["guard"] for c in armed_post["candidates"]),
       "the expired guard never appears as a candidate")

print("== the credential calendar ==")
cal = core.credential_calendar()
ok(any(r["guard_id"] == "gd_demo_expired" for r in cal), "the expired card is on the calendar")
ok(all("DATE ALERT" in r["label"] for r in cal), "entries are date alerts")
out = agents.credential_sweep()
ok(out["alerts"] >= 1, "expiring credentials raise alerts")
for _ in range(10):  # drain the queue past the per-run limit
    if agents.credential_sweep()["alerts"] == 0:
        break
ok(agents.credential_sweep()["alerts"] == 0,
   "once alerted, the 14-day cooldown holds — no re-nags")

print("== drafted copy ==")
cc = agents._coverage_copy({"from": "Harbor Mall"})
ok("credential-verified" in cc and "never send anyone" in cc, "coverage copy states the gate")
ok("yourco" not in cc.lower(), "white-label")

print("== matrix ==")
for a in ("edit_incident_narrative", "fill_post_unqualified", "advise_use_of_force"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("advise_use_of_force", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no incident missed")
ok("DEPOSITION" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("lapses_caught" in r["recorded"], "lapses counted")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["The unedited-incident file"]["kind"] == "scenario", "the file is a scenario")

print("== recovered, counted ==")
base = core.recovered_this_week()
store.log_event("fill_post", "ps_demo_armed", "human:scheduler", "R1", {})
rec = core.recovered_this_week()
ok(rec["posts_filled"] == base["posts_filled"] + 1, "human fills counted")
ok(rec["incidents_recorded"] >= 1, "incidents counted from the register")
ok(rec["credential_alerts"] >= 1, "alerts counted from the log")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
