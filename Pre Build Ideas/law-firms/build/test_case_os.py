#!/usr/bin/env python3
"""Case OS — the honesty suite. Every assertion pins a refusal."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ["CASEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="caseos_test_")

import agents, core, seed                    # noqa: E402
from core import gate, store                 # noqa: E402
from _kit.store import iso, now              # noqa: E402

P = F = 0


def ok(c, l):
    global P, F
    if c:
        P += 1
    else:
        F += 1
        print(f"  FAIL: {l}")


def section(t):
    print(f"\n{t}")


section("the UPL stop — no legal question is ever answered")
for t in ["do I have a case?", "what's my case worth", "how much will I get",
          "should I settle", "whose fault is it", "can I sue the store",
          "what are my chances", "am I going to win",
          "should I sign what the adjuster sent"]:
    ok(core.legal_question(t)["is_legal"], f"'{t}' is a legal question")
for t in ["what time is my appointment", "I moved, here's my new address",
          "did you get my records", "who is my paralegal"]:
    ok(not core.legal_question(t)["is_legal"], f"'{t}' is routine")
e = core.eval_upl()
ok(e["costly_missed"] == 0, "zero legal questions treated as routine")
ok(e["costly_recall"] == 1.0, "recall on legal questions is reported alone and is 1.0")
ok(core.MATRIX.rung_for("legal_advice")["rung"] == "R0", "legal advice is declared R0")
ok("legal_advice" in core.MATRIX.never_promote(), "and never promotes")
ok(core.MATRIX.promotable("legal_advice", streak=10**6)["promote"] is False, "no streak promotes it")
ok("send_retainer" in core.MATRIX.never_promote(), "sending a fee agreement never promotes")
ok("draft_demand_facts" in core.MATRIX.never_promote(), "a demand draft never leaves the gate")

section("the conflict check runs first and stops everything")
clients = [{"id": "c1", "name": "Rita Alvarez"}]
matters = [{"id": "m1", "client_name": "Rita Alvarez", "opposing": "Walton Pryce"}]
c = core.conflict_check("Walton Pryce", "Someone Else", matters, clients)
ok(not c["clear"], "a person we are already adverse to is a conflict")
c2 = core.conflict_check("New Person", "Rita Alvarez", matters, clients)
ok(not c2["clear"], "an opposing party who is our client is a conflict")
c3 = core.conflict_check("Fresh Caller", "Nobody Known", matters, clients)
ok(c3["clear"], "an unrelated caller is clear")

section("screening — unevaluable goes to a human, never to a guess")
cfg = {"accepted_types": ["auto", "premises"], "states": ["NC"]}
good = {"case_type": "auto", "state": "NC", "incident_date": iso(now() - timedelta(days=10)),
        "liability_facts": True, "treated": True, "coverage": "policy"}
ok(core.screen(good, cfg)["verdict"] == "qualified", "a clean lead qualifies")
ok(core.screen(dict(good, state="VA"), cfg)["verdict"] == "declined", "out of state declines")
ok(core.screen(dict(good, case_type="workers_comp"), cfg)["verdict"] == "declined",
   "a case type the firm does not take declines")
ok(core.screen(dict(good, coverage="none"), cfg)["verdict"] == "declined", "no coverage declines")
nod = core.screen(dict(good, incident_date=None), cfg)
ok(nod["verdict"] == "human_review", "no incident date cannot be evaluated, so a human does it")
ok(nod["unknown"], "and the unevaluable criterion is named")
stale = core.screen(dict(good, incident_date=iso(now() - timedelta(days=1600))), cfg)
ok(stale["verdict"] == "declined", "an expired statute declines")
ok(any("DATE ALERT" in r["why"] for r in stale["results"]),
   "and the statute check calls itself a date alert, not legal advice")

section("a production is not complete because a PDF arrived")
req = {"date_from": iso(now() - timedelta(days=180)), "date_to": iso(now()),
       "requested": ["records", "billing"], "patient_name": "Dana Reyes"}
whole = {"date_from": req["date_from"], "date_to": req["date_to"], "has_billing": True,
         "patient_name": "Dana Reyes"}
ok(core.verify_production(req, whole)["complete"], "a whole production verifies")
ok(not core.verify_production(req, dict(whole, has_billing=False))["complete"],
   "no billing is not complete — a demand without bills is not a demand")
ok(not core.verify_production(req, dict(whole, date_from=iso(now() - timedelta(days=60))))["complete"],
   "records that start late are not complete")
ok(not core.verify_production(req, {"has_billing": True, "patient_name": "Dana Reyes"})["complete"],
   "a production with no stated date range is not complete")
wrong = core.verify_production(req, dict(whole, patient_name="Someone Else"))
ok(any(g["severity"] == "critical" for g in wrong["gaps"]), "the wrong patient is critical")
ok(not core.verify_production(req, dict(whole, illegible_pages=3))["complete"],
   "illegible pages are a gap")
pe = core.eval_productions()
ok(pe["costly_missed"] == 0, "zero incomplete productions marked verified")
ok(pe["costly_recall"] == 1.0, "recall on 'incomplete' is reported alone and is 1.0")

section("a fact without a citation is omitted, never written")
store.save("productions", [{"id": "p1", "matter_id": "m9", "verified": True, "entries": [
    {"date": iso(now()), "what": "MRI", "charge": 1850, "exhibit": "C", "page": 12},
    {"date": iso(now()), "what": "Chiro (referenced only)", "charge": 480}]}])
ch = core.build_chronology("m9")
ok(len(ch["entries"]) == 1, "only the cited entry makes the draft")
ok(len(ch["unsupported"]) == 1, "the uncited one is listed as unsupported")
ok(ch["billed_total"] == 1850, "the billed total counts only what we can point to")
ok("FOR ATTORNEY REVIEW" in ch["note"] or "ATTORNEY REVIEW" in ch["note"],
   "the draft labels itself for attorney review")
ok("states no case value" in ch["note"], "and states no case value")

section("numbers that cannot be computed are blank")
store.wipe()
ok(core.completeness("nope").get("_missing"), "a matter with no records requests is UNKNOWN, not 0%")
ok(core.automation().get("_missing"), "an empty log → no automation rate")
ok(core._aging([]).get("_missing"), "too few sent requests → no median age")
r = core.roi({})
ok(all(l["value"] is None for l in r["lines"]), "with no inputs every ROI line is blank")
r2 = core.roi({"after_hours_leads_yr": 100, "incremental_sign_rate": 0.08, "avg_case_fee": 9000,
               "rescued_per_year": 6})
fee_line = [l for l in r2["lines"] if l["label"].startswith("Speed")][0]
ok("YOURS" in fee_line["assumption"] and "settlement statistic" in fee_line["assumption"],
   "the case-fee line refuses a borrowed settlement statistic on its face")
scen = [l for l in r2["lines"] if l["kind"] == "scenario"][0]
ok("SCENARIO, not a saving" in scen["note"],
   "screening quality is a scenario — you cannot count cases you did not take")
ok(r2["totals"]["scenario"]["total"] != r2["totals"]["revenue"]["total"],
   "and it is subtotalled apart from revenue")

section("the seeded firm, end to end")
st = seed.build(120, 12)
ok(st["matters"] == 120 and st["records"] > 100, "the seed builds a docket")

conflict_lead = store.by_id("leads", "ld_demo_conflict")
ok(conflict_lead, "the seed includes a conflicted lead")
out = agents.intake("ld_demo_conflict")
ok(out["steps"][0]["action"] == "conflict_stop", "the conflicted lead is stopped")
ok("refused" in out["steps"][0], "and it records that no facts were taken")
ok("screen" not in out, "no screening happened after the conflict hit")

legal = agents.intake("ld_demo_2")
ok(any(s["action"] == "route_to_attorney" for s in legal["steps"]),
   "the 'what's my case worth' lead is routed to an attorney")
ok(all("worth" not in (s.get("said") or "") for s in legal["steps"]),
   "and no reply mentions what it might be worth")

nodate = agents.intake("ld_demo_3")
ok(nodate["screen"]["verdict"] == "human_review", "the lead with no incident date goes to a human")

oos = agents.intake("ld_demo_4")
ok(oos["screen"]["verdict"] == "declined", "the out-of-state lead declines")
ok(store.by_id("leads", "ld_demo_4").get("decline_reason"),
   "and the reason is recorded so the firm can audit its own screening")

good_lead = agents.intake("ld_demo_1")
ok(any(s["action"] == "send_retainer" for s in good_lead["steps"]), "the qualifying lead gets a retainer")

agents.run_all()
evs = store.load("events")
ok(all(not (e["actor"].startswith("agent:") and not e.get("rung")) for e in evs),
   "no agent action is logged without a rung")
ok(not any(e["kind"] == "legal_advice" and e["rung"] not in ("R0",) for e in evs),
   "no legal-advice event ever executed above R0")

board = core.case_board()
unknown = [r for r in board["rows"] if r["completeness"].get("_missing")]
ok(unknown, "matters with no records requests report completeness as unknown, not 0%")

pend = gate.pending()
ok(any(a["action"] == "records_prepay" for a in pend), "every prepayment waits for a human")
ids = [e["id"] for e in store.load("events")]
agents.records_engine()
ok([e["id"] for e in store.load("events")][:len(ids)] == ids, "the event log is append-only")

section("R0 is not a slow yes — it never becomes an approvable row")
_before = len(gate.pending())
_r = gate.act("legal_advice", "intake", "r0_probe", {"summary": "probe"})
ok(_r.get("refused") is True and _r.get("executed") is False,
   "an R0 action returns a refusal, not a queued approval")
ok(len(gate.pending()) == _before,
   "and it adds nothing to the approval queue — a human must not be offered a button "
   "that clicks past a prohibition")
ok(any(e["kind"] == "refused" and (e.get("detail") or {}).get("action") == "legal_advice"
       for e in store.load("events")),
   "the refusal is recorded in the append-only log")

print(f"\n{P} passed, {F} failed")
sys.exit(1 if F else 0)
