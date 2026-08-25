#!/usr/bin/env python3
"""Shift OS — the honesty suite. Every assertion pins a refusal."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ["SHIFTOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="shiftos_test_")

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


section("the crisis stop — the worst failure this system could produce")
for t, kind in [("she fell in the bathroom and I can't get her up", "fall"),
                ("mom is complaining of chest pain", "cardiac"),
                ("he can't breathe properly, gasping", "respiratory"),
                ("she's unresponsive, won't wake up", "unresponsive"),
                ("suddenly confused and her face is drooping", "stroke_signs"),
                ("there's blood everywhere, it won't stop bleeding", "bleeding"),
                ("she said she wants to die", "self_harm"),
                ("there are bruises we can't explain and she's afraid of her son", "suspected_abuse")]:
    r = core.read_message(t)
    ok(r["tier"] == "crisis", f"'{t[:38]}…' is a crisis")
    ok(r["kind"] == kind, f"and is typed as {kind}")
e = core.eval_crisis()
ok(e["costly_missed"] == 0, "ZERO crisis messages were missed on the eval set")
ok(e["costly_recall"] == 1.0, "crisis recall is 1.0 and is reported alone")
ok("WORST FAILURE" in e["costly_note"], "the eval says out loud what the costly error is")

section("suspected abuse raises a mandatory-report flag the system never acts on")
r = core.read_message("there are bruises we can't explain and she's afraid of her son")
ok(r.get("mandatory_report") is True, "suspected abuse sets the flag")
ok(core.MATRIX.rung_for("mandatory_report")["rung"] == "R0", "and reporting is declared R0")
ok("mandatory_report" in core.MATRIX.never_promote(), "and never promotes")
ok("never made by software" in core.MANDATORY_REPORT_NOTE,
   "the note says reporting decisions are not made by software")

section("no clinical advice, ever")
for t in ["should she take her pill twice today?", "what is this new pill for",
          "her blood pressure was 180 over 100", "is that wound getting infected",
          "do you think she's getting worse", "can we change her care plan to add oxygen",
          "how many mg is that", "is it safe for her to walk alone"]:
    ok(core.read_message(t)["tier"] != "routine", f"'{t[:34]}…' is not answerable")
ok(core.read_message("")["tier"] == "clinical", "an empty message routes, never assumed harmless")
ok(core.read_message(None)["tier"] == "clinical", "an unreadable message routes")
ce = core.eval_clinical()
ok(ce["costly_missed"] == 0, "no clinical message was treated as routine")
ok(core.MATRIX.rung_for("clinical_answer")["rung"] == "R0", "clinical_answer is R0")
ok("clinical_answer" in core.MATRIX.never_promote(), "and never promotes")
ok(core.MATRIX.promotable("clinical_answer", streak=10**6)["promote"] is False,
   "no streak promotes it")

section("routine questions are answerable")
for t in ["can we move Thursday to Friday", "what time is the visit tomorrow",
          "please send the invoice again", "the aide was 20 minutes late"]:
    ok(core.read_message(t)["tier"] == "routine", f"'{t[:30]}…' is routine")

section("a caregiver is never auto-assigned to an unapproved pairing")
pairings = [{"caregiver_id": "cg_1", "client_id": "cl_1", "state": "approved"},
            {"caregiver_id": "cg_2", "client_id": "cl_1", "state": "declined"}]
ok(core.pairing_approved("cg_1", "cl_1", pairings) is True, "an approved pairing reads approved")
ok(core.pairing_approved("cg_2", "cl_1", pairings) is False, "a declined one does not")
ok(core.pairing_approved("cg_9", "cl_1", pairings) is False, "and an unknown one does not")
ok(core.MATRIX.rung_for("assign_new_pairing")["rung"] == "R1", "a new pairing is gated")
ok("assign_new_pairing" in core.MATRIX.never_promote(), "and never promotes")

section("the fill engine shows overtime on any option that would trigger it")
client = {"id": "cl_1", "name": "A Client", "zone": "north", "care_plan": ["transfer", "bathing"],
          "preferred_caregivers": []}
shift = {"id": "sh_1", "client_id": "cl_1", "hours": 6, "starts_at": iso(now())}
cgs = [
    {"id": "cg_1", "name": "Approved Near", "skills": ["transfer", "personal_care"],
     "travel_minutes": {"north": 10}, "available": True, "pay_rate": 18.0,
     "short_notice_accepted": 3},
    {"id": "cg_2", "name": "Declined", "skills": ["transfer", "personal_care"],
     "travel_minutes": {"north": 10}, "available": True, "pay_rate": 18.0},
    {"id": "cg_3", "name": "No Skill", "skills": ["driving"], "travel_minutes": {"north": 5},
     "available": True, "pay_rate": 18.0},
    {"id": "cg_4", "name": "Too Far", "skills": ["transfer", "personal_care"],
     "travel_minutes": {"north": 90}, "available": True, "pay_rate": 18.0},
    {"id": "cg_5", "name": "New Pairing", "skills": ["transfer", "personal_care"],
     "travel_minutes": {"north": 12}, "available": True, "pay_rate": 20.0},
]
prior = [{"caregiver_id": "cg_1", "client_id": "cl_1", "state": "completed",
          # "now" is ALWAYS inside the current Mon-start week; any offset backwards
          # can cross the boundary just after Monday midnight (this failed at 00:30 Monday)
          "starts_at": iso(now()), "hours": 38}]
res = core.fill_candidates(shift, client, cgs, pairings=pairings, shifts=prior)
names = [r["name"] for r in res["ranked"]]
ok("Approved Near" in names, "the approved, nearby caregiver is ranked")
ok(res["ranked"][0]["approved_pairing"] is True, "and approved pairings rank first")
ok("New Pairing" in names, "a new pairing is OFFERED as an option")
newp = [r for r in res["ranked"] if r["name"] == "New Pairing"][0]
ok(newp["approved_pairing"] is False, "flagged as unapproved")
ok(any("NEW PAIRING" in x for x in newp["reasons"]), "with the words on the row")
blocked = {b["name"]: b["why"] for b in res["blocked"]}
ok("No Skill" in blocked and "care plan needs" in blocked["No Skill"],
   "a caregiver missing a care-plan skill is blocked with the reason")
ok("Too Far" in blocked and "over the" in blocked["Too Far"], "so is one over the travel line")
ok("Declined" in blocked and "declined" in blocked["Declined"],
   "and one the family previously declined")
ot = [r for r in res["ranked"] if r["name"] == "Approved Near"][0]
ok(ot["overtime_hours"] > 0, "the caregiver at 38h this week goes into overtime on a 6h shift")
ok(ot["overtime_cost"] > 0 and any("OVERTIME" in x for x in ot["reasons"]),
   "and the cost is on the row, not discovered on Friday")

section("retention watches signals but never messages a caregiver")
ok(core.MATRIX.rung_for("message_caregiver_retention")["rung"] == "R0",
   "messaging a caregiver about retention is R0")
ok("message_caregiver_retention" in core.MATRIX.never_promote(), "and never promotes")
cg = {"id": "cg_x", "name": "At Risk", "preferred_hours_week": 40,
      "last_office_contact": iso(now() - timedelta(days=45)), "declined_in_a_row": 4}
risk = core.retention_risk(cg, [])
ok(risk and risk["count"] >= 2, "a caregiver with multiple signals is surfaced")
ok(any(s["signal"] == "no_office_contact" for s in risk["signals"]), "including office silence")
quiet = core.retention_risk({"id": "cg_q", "name": "Fine",
                             "last_office_contact": iso(now() - timedelta(days=2)),
                             "declined_in_a_row": 0}, [])
ok(quiet is None, "a caregiver with no signals is not flagged")
nopref = core.retention_risk({"id": "cg_n", "name": "No Pref",
                              "last_office_contact": iso(now() - timedelta(days=2))}, [])
ok(nopref is None, "and no preferred-hours figure is invented for someone who never gave one")

section("EVV rules are configurable — no state is hardcoded")
ok("_source" in core.DEFAULT_EVV_RULES, "the default rule set names itself a default")
ok("replace with the state" in core.DEFAULT_EVV_RULES["_source"],
   "and says it must be replaced before go-live")
s = {"starts_at": iso(now()), "hours": 4}
ex = {e["type"] for e in core.evv_exceptions(s)}
ok({"missed_clock_in", "missed_clock_out", "no_notes"} <= ex, "a bare shift raises three exceptions")
ok("no_gps" not in ex, "GPS is not required under the default rules")
gps_rules = {**core.DEFAULT_EVV_RULES, "require_gps": True}
ok("no_gps" in {e["type"] for e in core.evv_exceptions(s, gps_rules)},
   "but it IS under a rule set that requires it — the rules drive the exceptions")
clean = core.evv_exceptions({"starts_at": iso(now()), "hours": 10, "clock_in": iso(now()),
                             "clock_out": iso(now() + timedelta(hours=10)), "notes": "x"})
ok(clean == [], "a fully documented visit raises nothing")
ok(all(e.get("billing") for e in core.evv_exceptions({"starts_at": iso(now()), "hours": 4})),
   "every exception names its billing consequence")

section("over-authorization is a client fact, not a per-visit exception")
store.save("authorizations", [
    {"id": "a1", "client_id": "cl_over", "authorized_hours": 40, "used_hours": 46},
    {"id": "a2", "client_id": "cl_near", "authorized_hours": 40, "used_hours": 38},
    {"id": "a3", "client_id": "cl_fine", "authorized_hours": 40, "used_hours": 12},
    {"id": "a4", "client_id": "cl_unknown", "authorized_hours": None, "used_hours": 30}])
drift = {d["client_id"]: d for d in core.authorization_drift()}
ok(drift["cl_over"]["state"] == "over", "a client past their cap is over")
ok(drift["cl_near"]["state"] == "near", "one inside 10% of it is near")
ok("cl_fine" not in drift, "one well inside it is not on the list")
ok(drift["cl_unknown"].get("_missing"), "and one with no authorized hours is unknowable, not fine")
ok(not any(e["type"] == "over_authorization"
           for e in core.evv_exceptions({"starts_at": iso(now()), "hours": 4})),
   "no VISIT is flagged over-authorization — flagging every visit once a client passed their cap "
   "turned most of the book into exceptions and buried the real documentation gaps")

section("numbers that cannot be computed are blank")
store.wipe()
ok(core.overtime_exposure([]).get("_missing"), "too few scheduled caregivers → no OT exposure")
ok(core.automation().get("_missing"), "an empty log → no automation rate")
r = core.roi({})
ok(all(l["value"] is None for l in r["lines"]), "with no inputs every ROI line is blank")
r2 = core.roi({"departures_per_year": 80, "replacement_cost": 3000, "prevention_share": 0.15})
scen = [l for l in r2["lines"] if l["kind"] == "scenario"][0]
ok("SCENARIO, NOT A SAVING" in scen["note"], "turnover calls itself a scenario on its face")
ok("cannot be counted" in scen["note"], "and says prevented departures cannot be counted")
ok(r2["totals"]["scenario"]["total"] != r2["totals"]["revenue"]["total"],
   "and it is never summed into revenue")

section("the seeded agency, end to end")
st = seed.build(60, 40, 8)
ok(st["caregivers"] == 60 and st["shifts"] > 300, "the seed builds an agency")

crisis_msg = [m for m in store.load("messages") if m.get("demo_tag") == "crisis — fall"][0]
out = agents.handle_message(crisis_msg["id"])
ok(out["steps"][0]["action"] == "route_crisis", "the fall message routes to a human")
ok("911" in out["steps"][0]["said"], "and the reply carries the emergency instruction")
ok("refused" in out["steps"][0], "and records that it did not assess, reassure or advise")

abuse = [m for m in store.load("messages") if m.get("demo_tag") == "suspected abuse"][0]
o2 = agents.handle_message(abuse["id"])
ok(o2["steps"][0].get("mandatory_report"), "the abuse message raises the mandatory-report note")

clin = [m for m in store.load("messages") if m.get("demo_tag") == "clinical — dosing"][0]
o3 = agents.handle_message(clin["id"])
ok(o3["steps"][0]["action"] == "route_clinical", "the dosing question is routed")
ok("twice" not in o3["steps"][0]["said"], "and the reply does not answer it")

demo_shift = store.by_id("shifts", "sh_demo")
co = agents.callout("sh_demo")
ok(co["wave_one"] is not None, "the callout builds a ranked list")
unapproved = next((c for c in co["wave_one"] + co["wave_two"] if not c["approved_pairing"]), None)
if unapproved:
    bad = agents.accept_fill("sh_demo", unapproved["caregiver_id"])
    ok(bad["filled"] is False and "never been approved" in bad["refused"],
       "an unapproved caregiver cannot fill the shift even when they say yes")
else:
    ok(True, "no unapproved candidate surfaced in this seed — the rule is unit-tested above")
approved = next((c for c in co["wave_one"] + co["wave_two"] if c["approved_pairing"]), None)
if approved:
    good = agents.accept_fill("sh_demo", approved["caregiver_id"])
    ok(good["filled"] is True, "an approved caregiver fills it")
    ok(good["time_to_fill_minutes"] is not None, "and time-to-fill is recorded")

agents.run_all()
evs = store.load("events")
ok(all(not (e["actor"].startswith("agent:") and not e.get("rung")) for e in evs),
   "no agent action is logged without a rung")
ok(not any(e["kind"] == "clinical_answer" and e["rung"] != "R0" for e in evs),
   "no clinical answer ever executed")
ok(not any(e["kind"] == "message_caregiver_retention" for e in evs),
   "no caregiver was ever messaged about retention")
ids = [e["id"] for e in evs]
agents.retention()
ok([e["id"] for e in store.load("events")][:len(ids)] == ids, "the event log is append-only")

section("R0 is not a slow yes — it never becomes an approvable row")
_before = len(gate.pending())
_r = gate.act("clinical_answer", "triage", "r0_probe", {"summary": "probe"})
ok(_r.get("refused") is True and _r.get("executed") is False,
   "an R0 action returns a refusal, not a queued approval")
ok(len(gate.pending()) == _before, "and it adds nothing to the approval queue")
ok(any(e["kind"] == "refused" and (e.get("detail") or {}).get("action") == "clinical_answer"
       for e in store.load("events")), "the refusal is recorded in the append-only log")

print(f"\n{P} passed, {F} failed")
sys.exit(1 if F else 0)
