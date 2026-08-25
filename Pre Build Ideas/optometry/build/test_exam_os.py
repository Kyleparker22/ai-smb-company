#!/usr/bin/env python3
"""Exam OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["EXAMOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="examos-test-")
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


# ---------------------------------------------------------------- triage + eval
for text, kind in [("flashes and floaters and now a dark curtain on the side", "retinal"),
                   ("splashed bleach cleaner in my eye at work", "chemical"),
                   ("woke up and can't see out of my left eye", "vision_loss"),
                   ("something stuck in my eye from grinding, pain and tearing", "trauma"),
                   ("painful red eye and I sleep in my contacts", "keratitis")]:
    c = core.read_message(text)
    ok(c["label"] == "emergency" and c["kind"] == kind, f"emergency typed as {kind}")

c = core.read_message("splashed bleach cleaner in my eye at work")
ok("Rinse the eye" in c["instruction"], "a chemical splash carries the irrigate-now instruction")
c = core.read_message("flashes and floaters and now a dark curtain")
ok("seen today" in c["instruction"], "a retinal signal carries the same-day instruction")

ok(core.read_message("is it normal for my eyes to be this dry with the new drops")["label"] == "clinical",
   "a dry-eye question is clinical")
ok(core.read_message("need to reorder contacts, running low")["label"] == "reorder",
   "a reorder classifies")
ok(core.read_message("can you send a copy of my prescription")["label"] == "rx_request",
   "an Rx request classifies")
ok(core.read_message("")["label"] == "human", "empty routes to a person")

ev = core.run_eval()
ok(ev["costly_label"] == "emergency" and ev["costly_missed"] == 0,
   f"zero missed ocular emergencies in the shipped eval ({ev['costly_missed']})")
ok("PERMANENT VISION LOSS" in ev["costly_note"], "the eval names the stake")

# ---------------------------------------------------------------- Rx discipline
store.wipe()
store.save("config", {"company": "t"})
chk = core.reorder_check({"cl_rx_expires": iso(now() + timedelta(days=100))})
ok(chk["ok"], "a current Rx may reorder (R1)")
chk = core.reorder_check({"cl_rx_expires": iso(now() - timedelta(days=30))})
ok(not chk["ok"] and "an exam renews a prescription, not a message" in chk["refused"],
   "an expired Rx refuses the reorder")
chk = core.reorder_check({})
ok(not chk["ok"] and "unknown prescription" in chk["refused"],
   "no expiry recorded → refused, never assumed current")

store.save("patients", [
    {"id": "p_exp", "name": "A", "status": "active",
     "cl_rx_expires": iso(now() - timedelta(days=30))},
    {"id": "p_cur", "name": "B", "status": "active",
     "cl_rx_expires": iso(now() + timedelta(days=200))},
])
store.save("messages", [
    {"id": "m1", "patient_id": "p_exp", "text": "need to reorder contacts, running low"},
    {"id": "m2", "patient_id": "p_cur", "text": "need to reorder contacts, running low"},
    {"id": "m3", "patient_id": "p_cur", "text": "can you send a copy of my prescription"},
])
r = agents.handle_message("m1")
ok(r["steps"][0]["action"] == "refuse_and_offer_exam", "the expired reorder refuses and offers an exam")
ok(any(e["detail"].get("action") == "refill_expired_rx"
       for e in store.events(kind="refused", subject="m1")), "the refusal is logged")
r = agents.handle_message("m2")
ok(r["steps"][0]["action"] == "draft_reorder", "the current reorder drafts at R1")
r = agents.handle_message("m3")
ok(r["steps"][0]["action"] == "draft_rx_release" and "never withholds" in r["steps"][0]["why"],
   "an Rx request drafts the release — the system never withholds")

# ---------------------------------------------------------------- recall
store.save("patients", [
    {"id": "l1", "name": "deep", "status": "active",
     "last_exam": iso(now() - timedelta(days=800)), "recalls": []},
    {"id": "l2", "name": "current", "status": "active",
     "last_exam": iso(now() - timedelta(days=100)), "recalls": []},
    {"id": "l3", "name": "inactive", "status": "inactive",
     "last_exam": iso(now() - timedelta(days=800)), "recalls": []},
])
lp = core.lapsed()
ok(len(lp) == 1 and lp[0]["patient"] == "l1", "only active lapsed patients list")
p = store.by_id("patients", "l1")
p["recalls"] = [{"at": iso(now() - timedelta(days=60))}] * core.MAX_RECALLS
ok(core.recall_plan(p)["action"] == "none", "the ladder is bounded")

# ---------------------------------------------------------------- capture floor
store.save("exams", [])
cr = core.capture_rate()
ok(cr.get("_missing") and "need 40" in cr["_missing"], "capture refuses below its floor")
exams = [{"id": f"e{i}", "patient_id": "x", "at": iso(now() - timedelta(days=10))} for i in range(50)]
store.save("exams", exams)
store.save("purchases", [{"id": f"pu{i}", "exam_id": f"e{i}"} for i in range(30)])
cr = core.capture_rate()
ok(cr["rate"] == 0.6 and "walkouts are the leak" in cr["note"], "capture is counted")

# ---------------------------------------------------------------- R0 probes
for action in ("clinical_answer", "refill_expired_rx", "modify_rx", "withhold_rx"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("clinical_answer", "refill_expired_rx", "modify_rx", "withhold_rx")
           for a in core.gate.pending()), "no R0 action reached the approval queue")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Lapsed patients reactivated"]["value"] is None,
   "the reactivation line is blank without the operator's show rate")
ok(labels["Emergency routing"]["kind"] == "scenario", "emergency routing is never monetized")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("got hit in the eye with a racquetball, vision is blurry", "emergency"),
                   ("are the new lenses supposed to feel this scratchy", "clinical"),
                   ("almost out of my dailies, need another box", "reorder"),
                   ("need my pd and the script for ordering glasses online", "rx_request")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

# ---------------------------------------------------------------- recall copy
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

p9 = {"id": "px9", "name": "Amara Diallo", "status": "active"}
store.upsert("patients", p9)
b1 = agents._recall_copy(p9, {"overdue_days": 40}, 1)
ok("Amara" in b1 and "renews your prescription" in b1,
   "touch 1 names the chart fact and the Rx rule")
b2 = agents._recall_copy(p9, {"overdue_days": 70}, 2)
ok("switched practices" in b2 and "no hard feelings" in b2, "touch 2 offers the honest exit")
b3 = agents._recall_copy(p9, {"overdue_days": 100}, 3)
ok("leave it here" in b3, "touch 3 closes gently")
for b in (b1, b2, b3):
    ok(not any(w in b.lower() for w in ("glaucoma", "blind", "disease", "risk your")),
       "recall copy never scares — no disease language")
ok("yourco" not in (b1 + b2 + b3).lower(), "white-label: no yourco name in outward copy")

# ---------------------------------------------------------------- recovered, counted
base = core.recovered_this_week()
store.log_event("draft_recall", "px9", "human:frontdesk", "R1", {})
store.log_event("draft_reorder", "px9", "human:frontdesk", "R1", {})
store.log_event("draft_booking", "px9", "human:frontdesk", "R1", {})
rec = core.recovered_this_week()
ok(rec["recalls_sent"] == base["recalls_sent"] + 1
   and rec["reorders_released"] == base["reorders_released"] + 1
   and rec["exams_booked"] == base["exams_booked"] + 1,
   "human sends are counted; agent drafts are not")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
