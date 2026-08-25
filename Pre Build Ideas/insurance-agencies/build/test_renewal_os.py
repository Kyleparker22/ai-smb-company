#!/usr/bin/env python3
"""Renewal OS — the honesty suite. Every assertion pins a refusal."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ["RENEWALOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="renewalos_test_")

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


section("a price comparison cannot render without its coverage diff")
cur = {"premium": 2000, "coverage": {"deductible": 1000, "limit": "250/500"}}
bare = {"premium": 1700}
c = core.comparison_sheet(cur, bare)
ok(c["renderable"] is False, "a quote with no coverage schedule cannot be shown")
ok("_missing" in c and "coverage" in c["_missing"], "and it says why")
full = {"premium": 1700, "coverage": {"deductible": 5000, "limit": "250/500"}}
c2 = core.comparison_sheet(cur, full)
ok(c2["renderable"] is True, "with a schedule it renders")
ok(any(d["field"] == "deductible" for d in c2["coverage_differences"]),
   "and the deductible difference is named, not buried under the savings")
ok(c2["savings"] == 300.0, "the saving is computed")
ok("present_comparison" in core.MATRIX.never_promote(),
   "presenting a comparison never leaves the gate")

section("no quoting, no binding, no coverage opinion")
for a in ("coverage_advice", "quote_or_bind", "issue_nonstandard_coi", "state_notice"):
    ok(core.MATRIX.rung_for(a)["rung"] == "R0", f"{a} is declared R0 — the system never does it")
    ok(a in core.MATRIX.never_promote(), f"{a} can never be promoted")
    ok(core.MATRIX.promotable(a, streak=10**6)["promote"] is False, f"no streak promotes {a}")

section("non-standard certificates are a hard stop")
for lang in ["Additional insured per written contract", "waiver of subrogation in favor of owner",
             "primary and non-contributory", "30 days written notice of cancellation",
             "per project aggregate", "including completed operations", "blanket endorsement"]:
    k = core.classify_certificate({"requested_language": lang, "prior_certificate": "c1"})
    ok(k["kind"] == "non_standard", f"'{lang[:32]}' must escalate")
ok(core.classify_certificate({"requested_language": "", "prior_certificate": None})["kind"]
   == "non_standard", "the first certificate for a holder is a human's")
ok(core.classify_certificate({"requested_language": "", "holder_language_attached": True,
                              "prior_certificate": "c1"})["kind"] == "non_standard",
   "unreadable attached language is not the same as routine")
ok(core.classify_certificate({"requested_language": "same as last year",
                              "prior_certificate": "c1"})["kind"] == "standard",
   "a genuine repeat is routine")
e = core.eval_coi()
ok(e["costly_missed"] == 0, "zero non-standard certificates classified as routine")
ok(e["costly_recall"] == 1.0, "recall on non_standard is reported alone and is 1.0")

section("the renewal diff")
exp = {"premium": 2180.0, "coverage": {"deductible": 2500, "roof": "replacement"}}
ren = {"premium": 2681.4, "coverage": {"deductible": 5000, "roof": "acv"},
       "carrier_reason": "rate_action"}
c = core.classify_renewal(exp, ren)
ok(round(c["premium_delta_pct"], 3) == 0.23, "the delta is computed")
ok(c["material"] and c["large"], "a 23% increase is material and large")
ok(len(c["coverage_changes"]) == 2, "both coverage moves are caught")
flat = core.classify_renewal(exp, {"premium": 2180.0, "coverage": {"deductible": 5000, "roof": "replacement"}})
ok(flat["material"] is True,
   "a coverage change with a FLAT premium is still material — that is the one clients find at claim time")
quiet = core.classify_renewal(exp, {"premium": 2220.0, "coverage": exp["coverage"]})
ok(quiet["material"] is False, "a 2% move with no coverage change is quiet")
noprem = core.classify_renewal({"coverage": {}}, {"premium": 900, "coverage": {}})
ok(noprem["premium_delta_pct"] is None and noprem["material"] is True,
   "an unknowable change is material by default — it goes to a human")
ok(core.classify_renewal(exp, {"premium": 2400, "coverage": exp["coverage"]})["cause"] == "unknown",
   "a carrier that states no reason yields 'unknown', never a guess")

section("cross-sell reads permitted factors only")
hh = {"id": "h1", "name": "X", "policy_age_days": 700, "prior_quote_declined": False,
      "life_event_recorded": None, "claim_free_years": 3}
pol = [{"household_id": "h1", "line": "auto", "premium": 1400, "active": True}]
base = core.cross_sell_score(hh, pol)["score"]
poisoned = dict(hh, name="Someone Else", zip_code="90210", age=64, gender="f",
                surname_origin="x", language="es", marital_status="single",
                credit_band="low", neighborhood="north")
ok(core.cross_sell_score(poisoned, pol)["score"] == base,
   "adding age, gender, ZIP, language, marital status or credit does NOT move the score")
ok(core.cross_sell_score(dict(hh, life_event_recorded="new home"), pol)["score"] > base,
   "a recorded life event does move it")
ok(core.cross_sell_score(dict(hh, prior_quote_declined=True), pol)["score"] < base,
   "a prior decline moves it down")
multi = core.cross_sell_score(hh, pol + [{"household_id": "h1", "line": "home", "premium": 1800,
                                          "active": True}])
ok(multi["score"] == 0.0, "an already-bundled household is not on the list")
nores = core.cross_sell_score({"id": "h2", "policy_age_days": None, "claim_free_years": None},
                              [{"household_id": "h2", "line": "auto", "premium": 900, "active": True}])
ok(any("not recorded" in w for w in nores["why"]),
   "missing data is stated in the reasons, never silently defaulted")

section("numbers that cannot be computed are blank")
store.wipe()
ok(core.retention().get("_missing"), "too few renewals → no retention rate")
ok(core.mono_line_share().get("_missing"), "no households → no mono-line share")
ok(core.coi_turnaround().get("_missing"), "too few certificates → no turnaround")
ok(core.automation().get("_missing"), "an empty log → no automation rate")
r = core.roi({})
ok(all(l["value"] is None for l in r["lines"]), "with no inputs every ROI line is blank")
r2 = core.roi({"renewals_per_year": 100, "retention_points_gained": 0.03,
               "avg_commission": 200, "persistency_years": 4})
line = [l for l in r2["lines"] if l["label"] == "Retention lift"][0]
ok(line["value"] == 100 * 0.03 * 200 * 4, "retention lift computes")
ok("COMPOUNDS" in line["assumption"],
   "and the compounding assumption is stated on the line, not buried")

section("the seeded agency, end to end")
st = seed.build(600, 12)
ok(st["policies"] > 600 and st["certificates"] > 200, "the seed builds a book")

w = agents.watchtower()
ok(w["material"], "material renewals are surfaced")
ok(all("FOR PRODUCER REVIEW" in m["body"] for m in w["material"]),
   "every material draft is addressed to a licensed producer")
demo = [m for m in w["material"] if m["policy"] == "pol_demo"]
ok(demo and round(demo[0]["delta_pct"], 2) == 0.23, "the +23% demo renewal is caught")
ok(demo[0]["coverage_changes"], "and its coverage moves are on the same row")

d = agents.coi_desk()
ok(any(x["id"] == "coi_demo_ai" for x in d["escalated"]),
   "the additional-insured request is escalated, not issued")
ok(all(x["id"] != "coi_demo_ai" for x in d["issued"]), "and never appears in the issued list")
ai = store.by_id("certificates", "coi_demo_ai")
ok(ai.get("issued_at") is None, "it has no issue timestamp")

evs = store.load("events")
ok(all(not (e["actor"].startswith("agent:") and not e.get("rung")) for e in evs),
   "no agent action is logged without a rung")
ok(not any(e["kind"] in ("coverage_advice", "quote_or_bind") for e in evs),
   "no agent ever emitted a coverage opinion or a quote")
ids = [e["id"] for e in evs]
agents.cross_sell()
ok([e["id"] for e in store.load("events")][:len(ids)] == ids, "the event log is append-only")

sent = [e for e in store.load("events") if e["kind"] == "renewal_call_sent"]
ok(all(e["actor"].startswith("human:") for e in sent), "anything SENT carries a human actor")

section("R0 is not a slow yes — it never becomes an approvable row")
_before = len(gate.pending())
_r = gate.act("coverage_advice", "watchtower", "r0_probe", {"summary": "probe"})
ok(_r.get("refused") is True and _r.get("executed") is False,
   "an R0 action returns a refusal, not a queued approval")
ok(len(gate.pending()) == _before,
   "and it adds nothing to the approval queue — a human must not be offered a button "
   "that clicks past a prohibition")
ok(any(e["kind"] == "refused" and (e.get("detail") or {}).get("action") == "coverage_advice"
       for e in store.load("events")),
   "the refusal is recorded in the append-only log")

print(f"\n{P} passed, {F} failed")
sys.exit(1 if F else 0)
