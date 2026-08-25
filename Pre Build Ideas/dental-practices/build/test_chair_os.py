#!/usr/bin/env python3
"""Chair OS — the honesty suite. Every assertion pins a refusal."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ["CHAIROS_DATA_ROOT"] = tempfile.mkdtemp(prefix="chairos_test_")

import agents, core, seed                      # noqa: E402
from core import gate, store                   # noqa: E402
from _kit.store import iso, now                # noqa: E402

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


section("no insurance determination — an unconfirmed benefit is never 'covered'")
pt = {"id": "t1", "coverage_active": True, "benefits_used": 300,
      "procedures_this_year": {"prophy": 0}, "months_enrolled": 24}
v = core.verify(pt, "keystone_admin", "crown")
ok(v["verdict"] == "unconfirmed", "a payer that does not answer yields 'unconfirmed'")
ok(all(f["value"] is None for f in v["fields"].values()), "and every field is None, not a default")
ok(all(f["_missing"] for f in v["fields"].values()), "each field says why")
ok(core.can_state_coverage(v) is False, "and coverage may not be stated to the patient")

no_enroll = dict(pt, months_enrolled=None)
v2 = core.verify(no_enroll, "meridian", "crown")
ok(v2["fields"]["waiting_ok"]["value"] is None,
   "no enrollment date makes a waiting period unknowable — never assumed satisfied")
ok(core.can_state_coverage(v2) is False, "so coverage still may not be stated")

v3 = core.verify(pt, "meridian", "prophy")
ok(v3["verdict"] == "confirmed" and core.can_state_coverage(v3),
   "when the payer answers every field, coverage may be stated")

used_up = dict(pt, procedures_this_year={"prophy": 2})
v4 = core.verify(used_up, "meridian", "prophy")
ok(v4["fields"]["frequency_ok"]["value"] is False, "a used-up frequency limit is reported as false")
ok(core.can_state_coverage(v4) is False, "and coverage is not stated on it")

v5 = core.verify(pt, "not_a_real_payer", "crown")
ok(v5["verdict"] == "unconfirmed", "an unknown payer confirms nothing")

e = core.eval_coverage()
ok(e["costly_missed"] == 0, "the eval records zero unconfirmed benefits reported as confirmable")
ok(e["costly_recall"] == 1.0, "recall on 'unconfirmed' is reported alone and is 1.0")

section("no clinical opinion, ever")
ok(core.MATRIX.rung_for("clinical_opinion")["rung"] == "R0",
   "forming a clinical opinion is declared R0 so the prohibition is visible")
ok("clinical_opinion" in core.MATRIX.never_promote(), "and can never be promoted")
ok(core.MATRIX.promotable("clinical_opinion", streak=10**6)["promote"] is False,
   "no streak promotes it")
ok("state_coverage" in core.MATRIX.never_promote(), "stating coverage never promotes either")
ok(core.MATRIX.rung_for("state_coverage")["rung"] == "R1", "and it is gated")

section("a hygiene opening cannot be filled with a crown")
rdh = {"provider_type": "rdh", "minutes": 60}
dds = {"provider_type": "dds", "minutes": 90}
ok(core.fits(rdh, "crown")[0] is False, "a crown cannot go in a hygiene chair")
ok(core.fits(rdh, "prophy")[0] is True, "a prophy can")
ok(core.fits(dds, "implant")[0] is False, "a 120-minute implant does not fit a 90-minute opening")
ok(core.fits(dds, "crown")[0] is True, "a 90-minute crown does")
ok(core.fits(dds, "not_a_procedure")[0] is False, "an unknown procedure fits nothing")
ok("hygiene" in core.fits(rdh, "crown")[1] or "rdh" in core.fits(rdh, "crown")[1],
   "the refusal names the chair, so the office can argue with it")

section("the ranker shows its work and never invents a factor")
p_no_resp = {"id": "px", "name": "N R", "responsiveness": None, "benefit_year_end": None}
store.save("patients", [p_no_resp])
store.save("treatment_plan", [{"id": "tp1", "patient_id": "px", "procedure": "crown",
                               "state": "unscheduled", "diagnosed_at": iso(now())}])
r = core.rank_unscheduled()
ok(r and any("not recorded" in w for w in r[0]["why"]),
   "a missing responsiveness is stated in the reasons, not silently defaulted")
ok(any("not on file" in w for w in r[0]["why"]),
   "a missing benefit-year end is stated too")

section("numbers that cannot be computed are blank")
store.wipe()
ok(core.unscheduled_total().get("_missing"), "an empty ledger yields no total")
ok(core.automation().get("_missing"), "an empty log yields no automation rate")
ok(core.recovered().get("_missing"), "nothing attributable → nothing claimed as recovered")
ok(core.recall_due({"id": "x"}).get("_missing"),
   "a patient with no hygiene history is never called overdue")
r = core.roi({})
ok(all(l["value"] is None for l in r["lines"]), "with no inputs every ROI line is blank")

r2 = core.roi({"verifications_wk": 100, "minutes_each": 12, "loaded_rate": 25,
               "unscheduled_value": 1000000, "contact_rate": 0.5, "acceptance_rate": 0.3})
ok(r2["totals"]["time_saved"]["total"] is not None, "time saved computes")
ok(r2["totals"]["revenue"]["total"] == 150000.0, "revenue computes separately")
ok(r2["totals"]["revenue"]["total"] != r2["totals"]["revenue"]["total"] + r2["totals"]["time_saved"]["total"],
   "and the two are never summed into one headline")

section("the seeded practice, end to end")
st = seed.build(400, 12)
ok(st["patients"] == 400 and st["treatment_plan"] > 100, "the seed builds a practice with a ledger")

pack = agents.benefits_pack()
ok(pack["sheets"], "the pack assembles tomorrow's verifications")
ok(any(s["verdict"] != "confirmed" for s in pack["sheets"]),
   "and some of them honestly fail to confirm")
ok(all(not s["can_state_coverage"] for s in pack["sheets"] if s["verdict"] != "confirmed"),
   "no unconfirmed sheet is ever cleared to quote coverage")

fillres = agents.same_day_fill("ap_hole_rdh")
ok(all(core.PROCEDURES[c["procedure"]]["provider"] == "rdh" for c in fillres["wave_one"]),
   "the hygiene hole is only offered hygiene-chair treatment")
ok(fillres["rejected_sample"], "and what was refused is shown, with the reason")

bad = agents.accept_fill("ap_hole_rdh", next(
    t["id"] for t in store.load("treatment_plan")
    if t["procedure"] == "crown" and t["state"] == "unscheduled"))
ok(bad.get("booked") is False and bad.get("refused"),
   "booking a crown into a hygiene opening is refused even when asked directly")

agents.run_all()
evs = store.load("events")
ok(all(not (e["actor"].startswith("agent:") and not e.get("rung")) for e in evs),
   "no agent action is logged without a rung")
ids = [e["id"] for e in evs]
agents.recall_watchtower()
ok([e["id"] for e in store.load("events")][:len(ids)] == ids, "the event log is append-only")

pend = gate.pending()
ok(any(a["action"] == "draft_reactivation" for a in pend),
   "reactivation copy waits for a human")
sent = [e for e in store.load("events") if e["kind"] == "reactivation_sent"]
ok(all(e["actor"].startswith("human:") for e in sent), "anything SENT carries a human actor")

section("R0 is not a slow yes — it never becomes an approvable row")
_before = len(gate.pending())
_r = gate.act("clinical_opinion", "reactivation", "r0_probe", {"summary": "probe"})
ok(_r.get("refused") is True and _r.get("executed") is False,
   "an R0 action returns a refusal, not a queued approval")
ok(len(gate.pending()) == _before,
   "and it adds nothing to the approval queue — a human must not be offered a button "
   "that clicks past a prohibition")
ok(any(e["kind"] == "refused" and (e.get("detail") or {}).get("action") == "clinical_opinion"
       for e in store.load("events")),
   "the refusal is recorded in the append-only log")

print(f"\n{P} passed, {F} failed")
sys.exit(1 if F else 0)
