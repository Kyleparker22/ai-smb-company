#!/usr/bin/env python3
"""Carrier OS — the honesty suite. Every assertion pins a refusal."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ["CARRIEROS_DATA_ROOT"] = tempfile.mkdtemp(prefix="carrieros_test_")

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


ref = now()
CLEAN = dict(id="c1", name="Clean", authority_status="active",
             authority_since=iso(ref - timedelta(days=1500)),
             authority_checked_at=iso(ref),
             insurance_expires=iso(ref + timedelta(days=200)),
             insurance_checked_at=iso(ref), cargo_limit=100000,
             safety_checked_at=iso(ref), oos_rate=0.04, contact_checked_at=iso(ref),
             phone="555-0100", registered_phone="555-0100",
             email_domain="clean.example", registered_domain="clean.example",
             address="1 Main", registered_address="1 Main", domain_age_days=2000,
             equipment=["van"], loads_with_us=30, claims_with_us=0)
LOAD = {"value": 60000, "equipment": "van", "deliver_by": iso(ref + timedelta(days=3)),
        "offer_rate": 2400, "lane": "ATL-CHI"}

section("the asymmetry — refusal is autonomous, approval never is")
ok(core.MATRIX.rung_for("refuse_carrier")["rung"] == "R3",
   "refusing a carrier is autonomous — the safe direction")
ok(core.MATRIX.rung_for("approve_carrier")["rung"] == "R1", "approving one is gated")
ok("approve_carrier" in core.MATRIX.never_promote(), "and can never be promoted")
ok("release_load" in core.MATRIX.never_promote(), "releasing a load never promotes")
ok("dispatch" in core.MATRIX.never_promote(), "dispatching never promotes")
ok(core.MATRIX.promotable("approve_carrier", streak=10**6, calibration_ok=True)["promote"] is False,
   "a million clean approvals still cannot promote the approval action")
ok(core.MATRIX.rung_for("assert_fraud")["rung"] == "R0",
   "asserting fraud is declared R0 — the system never does it")
ok("assert_fraud" in core.MATRIX.never_promote(), "and never promotes")

section("every tripwire fires on its pattern and stays quiet otherwise")
e = core.eval_tripwires()
ok(e["costly_missed"] == 0, "no tripwire missed its own pattern")
ok(e["costly_recall"] == 1.0, "recall on 'should_fire' is reported alone and is 1.0")
for name, r in e["per_tripwire"].items():
    ok(r["fires_on_its_pattern"], f"{name} fires on its pattern")
    ok(r["quiet_otherwise"], f"{name} stays quiet on a clean carrier")

section("hard stops are refusals, not low scores")
for mutation, tw in [
        (dict(authority_status="revoked"), "authority_not_active"),
        (dict(insurance_expires=iso(ref + timedelta(days=1))), "insurance_expires_in_transit"),
        (dict(cargo_limit=25000), "cargo_below_value")]:
    fired = core.run_tripwires({**CLEAN, **mutation}, LOAD, {})
    hit = [f for f in fired if f["tripwire"] == tw]
    ok(hit and hit[0]["hard_stop"], f"{tw} is a hard stop")
ok(core.run_tripwires(CLEAN, LOAD, {"benchmark": {"median": 2500}}) == [],
   "a clean carrier on a fair rate fires nothing")

section("staleness is de-rated, never treated as current")
ok(core.freshness(iso(ref))["weight"] == 1.0, "a check from today is full weight")
ok(core.freshness(iso(ref - timedelta(days=30)))["weight"] < 1.0, "a 30-day-old check is de-rated")
ok(core.freshness(iso(ref - timedelta(days=400)))["weight"] == 0.2,
   "a 400-day-old check is heavily de-rated")
ok(core.freshness(None)["weight"] == 0.0, "a component never checked contributes nothing")
ok("never checked" in core.freshness(None)["label"], "and says so")
fresh = core.trust_file(CLEAN, LOAD, ref)["score"]
stale = core.trust_file({**CLEAN, "authority_checked_at": iso(ref - timedelta(days=300)),
                         "safety_checked_at": iso(ref - timedelta(days=300))}, LOAD, ref)["score"]
ok(fresh > stale,
   "the same good facts checked 300 days ago score LOWER — stale evidence pulls toward unknown, "
   "it does not merely count for less")
never = core.trust_file({**CLEAN, "authority_checked_at": None, "safety_checked_at": None,
                         "insurance_checked_at": None, "contact_checked_at": None}, LOAD, ref)
ok(never["score"] < fresh, "and a file with nothing checked scores below a checked one")
ok(any("never checked" in n for n in never["notes"]), "with the gap stated in the notes")

section("a file with nothing checked has no score")
bare = {"id": "c0", "name": "Unknown", "loads_with_us": 0}
tf = core.trust_file(bare, LOAD, ref)
ok(tf["score"] is not None or tf.get("_missing"),
   "either a score or an explicit refusal — never a silent zero")
ok(any("never hauled for us" in n for n in tf["notes"]),
   "and the absence of history is stated in the notes")

section("the benchmark refuses a thin lane")
store.wipe()
store.save("loads", [{"id": f"l{i}", "lane": "THIN", "equipment": "van", "carrier_rate": 1000,
                      "booked_at": iso(ref)} for i in range(3)])
b = core.benchmark("THIN", "van", ref)
ok(b.get("_missing") and "need" in b["_missing"], "three loads is not a benchmark, and it says so")
store.save("loads", [{"id": f"l{i}", "lane": "FAT", "equipment": "van",
                      "carrier_rate": 1000 + i * 10, "booked_at": iso(ref)} for i in range(12)])
b2 = core.benchmark("FAT", "van", ref)
ok(b2.get("median") is not None and b2["n"] == 12, "twelve loads gives a benchmark")
low = core.tw_rate_implausibly_low(CLEAN, {**LOAD, "offer_rate": 500}, {"benchmark": b2})
ok(low, "an implausibly low offer fires against a real benchmark")
ok(core.tw_rate_implausibly_low(CLEAN, {**LOAD, "offer_rate": 500},
                                {"benchmark": {"_missing": "thin"}}) is None,
   "and stays silent when there is no benchmark — it does not invent one to fire against")

section("numbers that cannot be computed are blank")
store.wipe()
ok(core.automation().get("_missing"), "an empty log → no automation rate")
r = core.roi({})
ok(all(l["value"] is None for l in r["lines"]), "with no inputs every ROI line is blank")
r2 = core.roi({"loads_flagged_yr": 12, "exposure_per_event": 40000, "loads_wk": 140,
               "vetting_minutes_saved": 15, "loaded_rate": 30})
scen = [l for l in r2["lines"] if l["kind"] == "scenario"][0]
ok("SCENARIO, NOT A SAVING" in scen["note"], "fraud exposure calls itself a scenario on its face")
ok("cannot be counted" in scen["note"], "and says prevented incidents cannot be counted")
ok(r2["totals"]["scenario"]["total"] != r2["totals"]["revenue"]["total"],
   "and it is never summed into revenue")

section("the seeded brokerage, end to end")
st = seed.build(20, 40)
ok(st["carriers"] == 20 and st["loads"] > 800, "the seed builds a brokerage with a year of history")

t = agents.triage("ld_demo")
ok(not t["benchmark"].get("_missing"), "the demo lane has enough history to benchmark")
hijack = [o for o in t["offers"] if o["carrier"] == "Northpine Trucking LLC"][0]
ok(hijack["tripwires"], "the hijacked-identity carrier fires tripwires")
ok("contact_mismatch" in hijack["tripwires"], "including the contact mismatch")
ok("recent_domain_change" in hijack["tripwires"], "and the fresh domain")
rebroker = [o for o in t["offers"] if o["carrier"] == "Swiftline Capacity Partners"][0]
ok("cargo_below_value" in rebroker["tripwires"], "the re-broker's cargo limit is below the load value")
ok(rebroker["hard_stop"], "which is a hard stop")

v = agents.vet("ca_hijack", "ld_demo")
ok(v["verdict"] == "refused", "the hijacked carrier is refused")
ok("NOT an assertion" in v["note"], "and the refusal explicitly is not a fraud assertion")
refusals = [e for e in store.load("events") if e["kind"] == "refuse_carrier"]
ok(refusals and all(e["actor"].startswith("agent:") and e["rung"] == "R3" for e in refusals),
   "refusals executed autonomously at R3")

clean_v = agents.vet("ca_1", "ld_demo")
ok(clean_v["verdict"] == "clean_for_human", "a clean carrier is 'clean for a human', not approved")
ok(clean_v["gate"]["executed"] is False, "the approval did NOT execute")
ok(clean_v["gate"].get("approval"), "it created a decision row instead")
approved = [e for e in store.load("events")
            if e["kind"] == "approve_carrier" and e["actor"].startswith("agent:")]
ok(not approved, "no agent has ever approved a carrier in this log")

released = [e for e in store.load("events") if e["kind"] == "release_load"
            and e["actor"].startswith("agent:")]
ok(not released, "and no agent has ever released a load")

agents.run_all()
evs = store.load("events")
ok(all(not (e["actor"].startswith("agent:") and not e.get("rung")) for e in evs),
   "no agent action is logged without a rung")
ok(not any(e["kind"] == "assert_fraud" and e["rung"] != "R0" for e in evs),
   "no fraud assertion ever executed")
ids = [e["id"] for e in evs]
agents.check_calls()
ok([e["id"] for e in store.load("events")][:len(ids)] == ids, "the event log is append-only")

notes = [e for e in store.load("events") if e["kind"] == "notify_customer"]
ok(all(e["rung"] == "R1" for e in notes) or not notes,
   "every customer notification is gated — what a customer is told is the broker's word")

section("R0 is not a slow yes — it never becomes an approvable row")
_before = len(gate.pending())
_r = gate.act("assert_fraud", "vetting", "r0_probe", {"summary": "probe"})
ok(_r.get("refused") is True and _r.get("executed") is False,
   "an R0 action returns a refusal, not a queued approval")
ok(len(gate.pending()) == _before, "and it adds nothing to the approval queue")
ok(any(e["kind"] == "refused" and (e.get("detail") or {}).get("action") == "assert_fraud"
       for e in store.load("events")), "the refusal is recorded in the append-only log")

print(f"\n{P} passed, {F} failed")
sys.exit(1 if F else 0)
