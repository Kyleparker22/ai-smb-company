#!/usr/bin/env python3
"""Visit OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["VISITOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="visitos-test-")
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


# ---------------------------------------------------------------- triage
for text, kind in [("my dog just ate a bar of baker's chocolate", "toxin"),
                   ("he keeps retching but nothing comes up, belly swollen", "gdv"),
                   ("cat straining in the litter box and nothing, crying", "blocked"),
                   ("she's gasping and her tongue looks blue", "breathing"),
                   ("he collapsed on the walk", "collapse"),
                   ("she got hit by a car", "trauma"),
                   ("pale gums and very weak", "pale_gums")]:
    c = core.read_message(text)
    ok(c["label"] == "emergency" and c["kind"] == kind, f"emergency typed as {kind}")
    ok(c.get("instruction") == core.EMERGENCY_INSTRUCTION, f"{kind} carries the ER instruction")

ok(core.read_message("what dose of benadryl for a 40lb dog")["label"] == "clinical",
   "a dosing question is clinical")
ok(core.read_message("I think it might be time to put her to sleep")["label"] == "qol",
   "euthanasia language is QoL")
ok(core.read_message("can I book a nail trim saturday")["label"] == "routine", "booking is routine")
ok(core.read_message("")["label"] == "human", "empty routes to a human")

ev = core.run_eval()
ok(ev["costly_label"] == "emergency" and ev["costly_missed"] == 0,
   f"zero missed emergencies in the shipped eval ({ev['costly_missed']})")
ok("DEAD PATIENT" in ev["costly_note"], "the eval names the stake")

# ---------------------------------------------------------------- handling behaviour
store.wipe()
store.save("config", {"company": "t"})
store.save("messages", [
    {"id": "m_e", "text": "my dog ate rat poison an hour ago"},
    {"id": "m_c", "text": "is it normal for him to limp after his shots"},
    {"id": "m_q", "text": "we're thinking about quality of life for our old girl"},
])
r = agents.handle_message("m_e")
ok(r["steps"][0]["action"] == "route_emergency", "an emergency routes immediately")
ok(core.EMERGENCY_INSTRUCTION in r["steps"][0]["said"], "the reply is the ER instruction, nothing else")
r = agents.handle_message("m_c")
ok(r["steps"][0].get("refused") == "routed unanswered", "clinical goes to a DVM unanswered")
ok(any(e["kind"] == "refused" and e["detail"]["action"] == "clinical_answer"
       for e in store.events(subject="m_c")), "the clinical refusal is logged")
r = agents.handle_message("m_q")
ok("no automated reply" in r["steps"][0]["refused"], "QoL gets no automated reply of any kind")

# ---------------------------------------------------------------- the deceased exclusion
store.save("patients", [
    {"id": "p_a", "client_id": "c1", "name": "Biscuit", "species": "dog", "status": "active",
     "annual_due": iso(now() - timedelta(days=100)), "reminders": []},
    {"id": "p_d", "client_id": "c1", "name": "Scout", "species": "dog", "status": "deceased",
     "annual_due": iso(now() - timedelta(days=200)), "reminders": []},
    {"id": "p_t", "client_id": "c1", "name": "Milo", "species": "cat", "status": "transferred",
     "vaccines_due": iso(now() - timedelta(days=90)), "reminders": []},
])
lp = core.lapsed()
ok(len(lp) == 1 and lp[0]["patient"] == "p_a",
   "only the active patient is visible to reactivation")
plan = core.reminder_plan(store.by_id("patients", "p_d"))
ok(plan["action"] == "refuse" and "never forgives" in plan["why"],
   "the deceased patient is refused again at plan time — defence in depth")

store.save("approvals", [])
out = agents.reactivation_sweep()
ok(out["drafted"] == 1, "the sweep drafts exactly the one active lapsed patient")
ok(not any(a["subject"] in ("p_d", "p_t") for a in store.load("approvals")),
   "no draft ever references a deceased or transferred patient")

# ladder bounds
p = store.by_id("patients", "p_a")
p["reminders"] = [{"at": iso(now() - timedelta(days=90))}] * core.MAX_REMINDERS
store.upsert("patients", p)
ok(core.reminder_plan(p)["action"] == "none", "the ladder is bounded")
p["reminders"] = [{"at": iso(now() - timedelta(days=5))}]
store.upsert("patients", p)
ok("cooldown" in core.reminder_plan(p)["why"], "cooldown respected")

# ---------------------------------------------------------------- waitlist
store.save("waitlist", [
    {"id": "w1", "patient_id": "p_a", "name": "Biscuit", "species": "dog",
     "minutes_needed": 30, "doctor_pref": None, "since": iso(now() - timedelta(days=8))},
    {"id": "w2", "patient_id": "p_d", "name": "Scout", "species": "dog",
     "minutes_needed": 30, "doctor_pref": None, "since": iso(now() - timedelta(days=3))},
    {"id": "w3", "patient_id": "p_a", "name": "Biscuit", "species": "dog",
     "minutes_needed": 60, "doctor_pref": None, "since": iso(now())},
])
r = core.rank_waitlist({"minutes": 30, "doctor": "Dr. Ashby"})
ok(any(c["waitlist_id"] == "w1" for c in r["candidates"]), "a fitting candidate ranks")
ok(any("never offered" in b["why"] for b in r["blocked"]),
   "the deceased patient is blocked from backfill with the reason named")
ok(any("needs 60m" in b["why"] for b in r["blocked"]), "a too-long visit is blocked by fit")

# ---------------------------------------------------------------- backfill stats floor
store.save("appointments", [])
bf = core.backfill_stats()
ok(bf.get("_missing") and "need 10" in bf["_missing"], "backfill rate refuses below its floor")

# ---------------------------------------------------------------- R0 probes
for action in ("clinical_answer", "qol_conversation", "contact_deceased"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("clinical_answer", "qol_conversation", "contact_deceased")
           for a in core.gate.pending()), "no R0 action reached the approval queue")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Lapsed patients reactivated"]["value"] is None,
   "revenue line blank without the operator's show rate")
sc = labels["After-hours emergencies routed right"]
ok(sc["kind"] == "scenario" and sc["value"] is None,
   "safety routing is never monetized — the line is the operator's or blank")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("she got into the easter lilies on the counter", "emergency"),
                   ("his gums look white and he won't get up", "emergency"),
                   ("we're wondering about her quality of life lately", "qol")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:40]} → {want}")

# ---------------------------------------------------------------- drafted copy
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

store.save("clients", [{"id": "cl9", "name": "Priya Raman"}])
p9 = {"id": "pt9", "client_id": "cl9", "name": "Biscuit", "species": "dog", "status": "active",
      "annual_due": _iso(_now() - timedelta(days=90))}
store.upsert("patients", p9)
row9 = {"patient": "pt9", "due": [{"item": "annual exam", "overdue_days": 90}]}
body = agents._reminder_copy(p9, row9, 1)
ok("Priya" in body and "Biscuit" in body and "annual exam" in body,
   "reminder copy names the client, the patient, and the chart's own due item")
ok("yourco" not in body.lower(), "white-label: no yourco name in outward copy")
ok(not any(w in body.lower() for w in ("sick", "risk", "danger", "worried")),
   "reminder copy never makes a health claim")
body3 = agents._reminder_copy(p9, row9, 3)
ok("last reminder" in body3.lower() and "leave it" in body3,
   "touch 3 closes the ladder without pressure")
body2 = agents._reminder_copy(p9, row9, 2)
ok("switched clinics" in body2, "touch 2 offers the honest exit — close the file properly")

offer = agents._offer_copy({"name": "Marta Oyelaran"}, {"minutes": 30, "when": "tomorrow 9:40",
                                                       "doctor": "Dr. Finch"})
ok("30-minute" in offer and "Dr. Finch" in offer and "first-come" in offer,
   "backfill offer carries slot facts and the wave rule")

# the sweep records the drafted body on the reminder
out = agents.reactivation_sweep(limit=5)
ok(out["drafted"] >= 1, "sweep drafts for the lapsed active patient")
p9 = store.by_id("patients", "pt9")
ok(p9.get("reminders") and p9["reminders"][0].get("body"), "the drafted body is recorded")

# ---------------------------------------------------------------- recovered, counted
rec = core.recovered_this_week()
ok(rec["reminders_sent"] == 0 and rec["slots_backfilled"] == 0,
   "nothing sent or filled → zeros, honestly")
store.log_event("reminder_sent", "pt9", "human:frontdesk", "R1", {})
store.upsert("appointments", {"id": "ap9", "when": "today", "minutes": 30,
                              "cancelled_at": _iso(_now() - timedelta(days=1)),
                              "backfilled_at": _iso(_now())})
p9["reactivated_at"] = _iso(_now() - timedelta(days=2))
store.upsert("patients", p9)
rec = core.recovered_this_week()
ok(rec["reminders_sent"] == 1 and rec["slots_backfilled"] == 1 and rec["patients_returned"] == 1,
   "sends, backfills, and returns are counted")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
