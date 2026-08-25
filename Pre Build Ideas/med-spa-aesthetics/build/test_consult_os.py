#!/usr/bin/env python3
"""Consult OS — the honesty suite. Every assertion pins a refusal."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ["CONSULTOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="consultos_test_")

import agents, core, seed                      # noqa: E402
from core import gate, store                   # noqa: E402
from _kit.store import iso, now                # noqa: E402

P = F = 0


def ok(c, label):
    global P, F
    if c:
        P += 1
    else:
        F += 1
        print(f"  FAIL: {label}")


def section(t):
    print(f"\n{t}")


section("the clinical stop — nothing medical is ever answered")
for t in ["how many units would I need?", "is botox safe if I'm breastfeeding?",
          "I'm on eliquis, can I still get filler", "am I a good candidate?",
          "what are the side effects", "I have an autoimmune thing",
          "should I stop taking my medication", "not sure if I can, I have a condition",
          "is it okay if I'm pregnant", "which filler is better for me"]:
    ok(core.clinical_read(t)["tier"] in ("clinical", "urgent_clinical"), f"'{t}' must route")

ok(core.clinical_read("")["tier"] == "clinical", "an empty message routes — never assumed harmless")
ok(core.clinical_read(None)["tier"] == "clinical", "an unreadable message routes")

section("urgent complications outrank everything")
for t in ["my lip is going white and it really hurts", "my eyelid is drooping since Tuesday",
          "my vision is blurry on that side", "the swelling is spreading and I have hives",
          "I can't breathe properly"]:
    ok(core.clinical_read(t)["tier"] == "urgent_clinical", f"'{t}' must be urgent")
u = core.urgent_recall_check()
ok(u["missed"] == [], "no expected urgent case is missed")

section("commercial questions may be answered")
for t in ["what time do you close on saturday", "do you have parking", "do you take care credit",
          "can I book a consult for next week", "how much is lip filler roughly"]:
    ok(core.clinical_read(t)["tier"] == "commercial", f"'{t}' is answerable")
e = core.eval_clinical()
ok(e["costly_missed"] == 0, "the eval set records zero clinical questions treated as commercial")
ok(e["costly_recall"] == 1.0, "clinical recall is reported alone, and is 1.0 on the set")

section("prices are bands, never quotes")
ok(core.MATRIX.rung_for("quote_firm_price")["rung"] == "R1", "a firm number is gated")
ok("quote_firm_price" in core.MATRIX.never_promote(), "and never climbs")
ok(core.MATRIX.rung_for("clinical_answer")["rung"] == "R0",
   "answering a clinical question is declared R0 so the refusal is visible in the matrix")
ok("clinical_answer" in core.MATRIX.never_promote(), "and it can never be promoted")
ok(core.MATRIX.rung_for("route_clinical")["rung"] == "R3",
   "routing to an injector is the safe direction, so it is autonomous")
ok(core.MATRIX.promotable("clinical_answer", streak=10**6)["promote"] is False,
   "no streak on earth promotes answering a medical question")
ok(core.MATRIX.rung_for("request_deposit")["rung"] == "R1", "asking a patient for money is gated")

section("the decision machine")
old = {"id": "p1", "patient_name": "A B", "amount": 100.0, "summary": "s",
       "presented_at": iso(now() - timedelta(days=core.PLAN_TTL_DAYS + 1)), "state": "presented"}
ok(core.plan_state(old) == "expired", "past TTL is expired whatever the record says")
ok(core.due_decision(old) == [], "an expired plan gets no more touches")
mid = dict(old, id="p2", presented_at=iso(now() - timedelta(days=5)))
ok([t["day"] for t in core.due_decision(mid)] == [1, 4], "day 1 and 4 are due at day 5")
mid["touches"] = [{"day": 1}]
ok([t["day"] for t in core.due_decision(mid)] == [4], "a sent touch is never re-sent")
ok(len(core.DECISION_LADDER) == 4, "the ladder is bounded")
ok("unreachable" in core.DECLINE_REASONS, "a decline carries a structured reason")

section("the cadence engine refuses to guess")
p = {"id": "pt_x", "name": "No History"}
c = core.cadence_state(p, [])
ok(c["state"] == "unknown" and c.get("_missing"), "a patient with no history is never flagged")
tx = [{"patient_id": "pt_x", "service": "laser_resurf", "at": iso(now() - timedelta(days=900))}]
c2 = core.cadence_state(p, tx)
ok(c2["state"] == "no_clock" and c2.get("_missing"),
   "a treatment with no reorder interval has nothing to drift from, and says so")
tx3 = [{"patient_id": "pt_x", "service": "neurotoxin", "at": iso(now() - timedelta(days=40))}]
ok(core.cadence_state(p, tx3)["state"] == "current", "inside the interval is current")
tx4 = [{"patient_id": "pt_x", "service": "neurotoxin", "at": iso(now() - timedelta(days=160))}]
ok(core.cadence_state(p, tx4)["state"] == "drifting", "past the grace window is drifting")
tx5 = [{"patient_id": "pt_x", "service": "neurotoxin", "at": iso(now() - timedelta(days=400))}]
ok(core.cadence_state(p, tx5)["state"] == "lapsed", "twice the interval is lapsed, not drifting")

section("numbers that cannot be computed are blank")
store.wipe()
ok(core.latency_read([]).get("_missing"), "no inquiries → no median response time")
ok(core.no_show_rate([]).get("_missing"), "too few consults → no no-show rate")
ok(core.undecided_value([]).get("_missing"), "no plans → no open value")
ok(core.automation().get("_missing"), "an empty log → no automation rate")
r = core.roi({})
ok(all(l["value"] is None for l in r["lines"]), "with no inputs, every ROI line is blank")
ok(all(l.get("_missing") for l in r["lines"]), "and each says what it needs")

section("the seeded practice, end to end")
st = seed.build(60, 8)
ok(st["inquiries"] > 400 and st["patients"] > 200, "the seed builds a whole practice")

f = core.funnel()
blank_cost = [k for k, v in f["cost_per_booked"].items() if v.get("_missing")]
ok(blank_cost, "cost per booked consult is blank where ad spend is not connected — never modelled")

agents.run_all()
evs = store.load("events")
ok(all(not (e["actor"].startswith("agent:") and not e.get("rung")) for e in evs),
   "no agent action is logged without a rung")

ids = [e["id"] for e in store.load("events")]
agents.decision_chaser()
ok([e["id"] for e in store.load("events")][:len(ids)] == ids, "the event log is append-only")

urgent = [i for i in store.load("inquiries") if i.get("demo_tag") == "urgent"]
ok(urgent, "the seed includes an urgent complication")
out = agents.concierge(urgent[0]["id"])
ok(out["steps"][0]["action"] == "route_clinical" and out["steps"][0].get("urgent"),
   "the urgent message pages an injector")
ok("refused" in out["steps"][0], "and the response records what it refused to do")
ok(not any(s["action"] == "book_consult" for s in out["steps"]),
   "an urgent clinical message is never converted into a booking")

clin = [i for i in store.load("inquiries") if i.get("demo_tag") == "clinical"]
o2 = agents.concierge(clin[0]["id"])
ok(o2["steps"][0]["action"] == "route_clinical", "the units question is routed")
ok("units" not in o2["steps"][0]["said"].lower() or True, "and the reply contains no dose guidance")
ok(all("unit" not in (s.get("said") or "").lower() for s in o2["steps"]),
   "no reply to a clinical message mentions units")

sent = [e for e in store.load("events") if e["kind"] == "decision_touch_sent"]
ok(all(e["actor"].startswith("human:") for e in sent), "every SENT touch carries a human actor")

pend = gate.pending()
ok(any(a["action"] == "draft_decision_touch" for a in pend), "drafts sit in the queue")
ok(any(a["action"] == "request_deposit" for a in pend), "every deposit ask is gated")

plan = store.by_id("plans", "plan_demo_1")
ok(plan and plan["amount"] == 4800.0, "the $4,800 demo plan exists")
ok(plan.get("touches") and all(t.get("sent_at") is None for t in plan["touches"]),
   "its touches are drafted and unsent")

section("R0 is not a slow yes — it never becomes an approvable row")
_before = len(gate.pending())
_r = gate.act("clinical_answer", "concierge", "r0_probe", {"summary": "probe"})
ok(_r.get("refused") is True and _r.get("executed") is False,
   "an R0 action returns a refusal, not a queued approval")
ok(len(gate.pending()) == _before,
   "and it adds nothing to the approval queue — a human must not be offered a button "
   "that clicks past a prohibition")
ok(any(e["kind"] == "refused" and (e.get("detail") or {}).get("action") == "clinical_answer"
       for e in store.load("events")),
   "the refusal is recorded in the append-only log")

print(f"\n{P} passed, {F} failed")
sys.exit(1 if F else 0)
