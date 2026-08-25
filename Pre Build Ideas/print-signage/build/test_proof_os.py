#!/usr/bin/env python3
"""Proof OS — the suite. `python3 test_proof_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["PROOFOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="proofos_test_")
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
ok(len(store.load("jobs")) >= 160, "jobs seeded")

print("== triage: approval reads first ==")
for text, want in (("looks good, go ahead and print it", "approval"),
                   ("approved! run it", "approval"),
                   ("ship it, we're happy with the last revision", "approval"),
                   ("here's the artwork attached as a pdf", "art_inbound"),
                   ("artwork enclosed, two versions to choose from", "art_inbound"),
                   ("need these by friday for the trade show, rush if you have to", "rush"),
                   ("can you do 500 flyers asap", "rush"),
                   ("the color is way off from what we approved", "complaint"),
                   ("the banner came out crooked on the grommet side", "complaint"),
                   ("", "human"),
                   ("what are your hours saturday", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:42]} → {want}")

print("== the proof gate ==")
okp, why = core.can_produce(store.by_id("jobs", "jb_demo_verbal"))
ok(not okp and "a note, not a gate pass" in why, "verbal go-ahead refused, quoted back")
ok("eaten reprint" in why, "the refusal names the stake")
r = agents.release_job("jb_demo_verbal")
ok("refused" in r, "release refuses")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "produce_without_proof_approval"
       for e in store.events()), "produce_without_proof_approval logged")
okp, why = core.can_produce(store.by_id("jobs", "jb_demo_approved"))
ok(okp and "rev 1 approved by Osei" in why, "a recorded approval opens the gate, cited")
r = agents.release_job("jb_demo_approved")
ok(r.get("rung") == "R1" and r.get("approval"), "the approved job queues at R1")

print("== the approval message becomes a record ==")
out = agents.handle_message("ms_demo_approve")
ok(out["steps"][0]["action"] == "record_approval", "the click is recorded")
j = store.by_id("jobs", "jb_demo_verbal")
ok(j["proof_approval"]["approved_by"] == "Mercer" and j["proof_approval"]["revision"] == 2,
   "who, and which revision")
okp, why = core.can_produce(j)
ok(okp, "the job can now produce — the record did it, not the phone call")

print("== the IP flag ==")
ip = core.ip_check(store.by_id("jobs", "jb_demo_ip"))
ok(ip["flagged"] and "nike" in ip["marks"], "the swoosh is flagged")
out = agents.handle_message("ms_demo_ip")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "approve_trademarked_art"
       for e in store.events()), "approve_trademarked_art refused + logged")
ok(not core.ip_check({"art_desc": "family reunion tee with a lake photo"})["flagged"],
   "clean art passes")

print("== capacity dates + rush displacement ==")
p = core.promise_date(8)
ok(p.get("date") and "arithmetic is shown" in p["note"], "a date computes with its arithmetic")
store.save("config", dict(store.load("config"), press_hours_per_day=None))
p2 = core.promise_date(8)
ok("_missing" in p2 and "guess with a calendar" in p2["_missing"],
   "no capacity → the date refuses")
store.save("config", dict(store.load("config"), press_hours_per_day=16))
disp = core.rush_displacement(6)
ok(len(disp["displaced"]) >= 1 and "a trade, not free speed" in disp["note"],
   "the rush names what it displaces")

print("== drafted copy ==")
job = {"customer_name": "Dana Mercer", "desc": "banner set"}
b1 = agents._chase_copy(job, 1)
ok("Dana" in b1 and "starts at\nthe click" in b1 or "starts at" in b1,
   "the chase says the clock starts at the click")
b3 = agents._chase_copy(job, 3)
ok("releases to other work" in b3, "touch 3 states the honest consequence")
cc = agents._complaint_copy({"from": "Osei"}, store.by_id("jobs", "jb_demo_approved"))
ok("revision 1" in cc and "reprint is on us" in cc,
   "with an approval the reply cites the revision and owns a true mismatch")
cc2 = agents._complaint_copy({"from": "Havel"}, {"id": "x"})
ok("we won't argue" in cc2, "without an approval the reply admits it instead of arguing")
rc = agents._rush_copy({"from": "Renner"}, disp)
ok("honest trade" in rc and "before they notice" in rc, "the rush copy names the trade")
ok("yourco" not in (b1 + b3 + cc + cc2 + rc).lower(), "white-label")

print("== the chase ladder ==")
j9 = {"id": "jb_x", "customer_name": "Pruitt", "desc": "window lettering", "value": 520,
      "proof_sent_at": iso(now() - timedelta(days=5))}
store.upsert("jobs", j9)
ok(core.chase_plan(j9)["action"] == "draft_chase", "a stalled proof is due a touch")
j9["chase_touches"] = [{"at": iso(now() - timedelta(days=1))}]
ok(core.chase_plan(j9)["action"] == "none", "2-day cooldown holds")
j9["chase_touches"] = [{"at": iso(now() - timedelta(days=9 - i * 3))} for i in range(3)]
ok("a person calls" in core.chase_plan(j9)["why"], "past the ladder, a person calls")

print("== matrix ==")
for a in ("produce_without_proof_approval", "promise_date_without_capacity",
          "approve_trademarked_art"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("produce_without_proof_approval", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no approval missed")
ok("EATEN REPRINT" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("waiting_value" in r["recorded"], "stalled value recorded")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Proof-stalled revenue released"]["kind"] == "cash_timing",
   "stalled revenue is cash timing, not new revenue")
ok(labels["Reprints avoided at the gate"]["kind"] == "scenario",
   "prevented reprints are a scenario, never counted")

print("== recovered, counted ==")
base = core.recovered_this_week()
store.log_event("draft_proof_chase", "jb_x", "human:frontdesk", "R1", {})
j9b = store.by_id("jobs", "jb_demo_approved")
j9b["produced_at"] = iso(now() - timedelta(days=1))
store.upsert("jobs", j9b)
rec = core.recovered_this_week()
ok(rec["chases_sent"] == 1, "human-sent chases counted; agent drafts are not")
ok(rec["jobs_produced"] == base["jobs_produced"] + 1, "produced jobs counted")
ok(rec["approvals_recorded"] >= 1, "recorded approvals counted")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
