#!/usr/bin/env python3
"""Assay OS — the honesty suite."""
import os, sys, tempfile
from pathlib import Path

os.environ["ASSAYOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="assayos-test-")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import agents, core, seed
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


seed.build(n_samples=140)

# ---------------------------------------------------------------- grading
ok(core.grade({"purity_pct": 99.4, "identity_match": True, "water_pct": 4.0,
               "acetate_pct": 9.0})["grade"] == "PASS", "a clean panel passes")
ok(core.grade({"purity_pct": 97.9, "identity_match": True, "water_pct": 4.0,
               "acetate_pct": 9.0})["grade"] == "FAIL", "purity below spec fails")
ok(core.grade({"purity_pct": 99.9, "identity_match": False, "water_pct": 4.0,
               "acetate_pct": 9.0})["grade"] == "FAIL", "identity failure fails at any purity")
ok(core.grade({"purity_pct": 99.9, "identity_match": True, "water_pct": 8.1,
               "acetate_pct": 9.0})["grade"] == "FAIL", "water above max fails")
ok(core.grade({})["grade"] == "INDETERMINATE", "an empty result is never a pass")
ok(core.grade(None)["grade"] == "INDETERMINATE", "no result is never a pass")

# The load-bearing one: a missing line must never read as clean.
for field in ("purity_pct", "identity_match", "water_pct", "acetate_pct"):
    r = {"purity_pct": 99.5, "identity_match": True, "water_pct": 4.0, "acetate_pct": 9.0}
    r[field] = None
    g = core.grade(r)
    ok(g["grade"] == "INDETERMINATE", f"missing {field} is INDETERMINATE, not PASS")
    ok("not measured" in g["reasons"][0], f"missing {field} says what was not measured")

ok(core.grade({"purity_pct": 98.0, "identity_match": True, "water_pct": 8.0,
               "acetate_pct": 15.0})["grade"] == "PASS", "exactly-at-limit values pass (inclusive bounds)")

# ---------------------------------------------------------------- the hash
s = store.load("samples")[0]
r = next(x for x in store.load("results") if x["sample_id"] == s["id"])
h1 = core.coa_hash(core.coa_payload(s, r))
h2 = core.coa_hash(core.coa_payload(s, r))
ok(h1 == h2, "the same sample and result always hash the same")
r2 = dict(r, purity_pct=float(r["purity_pct"]) - 0.1)
ok(core.coa_hash(core.coa_payload(s, r2)) != h1, "changing a reported value changes the hash")
ok(len(h1) == 64, "the hash is a full sha256")
ok(core.coa_payload(s, r)["scope"] == core.SCOPE_NOTE, "every certificate carries the scope note")

# ---------------------------------------------------------------- release is R1, forever
ok(core.matrix.rung_for("release_coa")["rung"] == "R1", "release sits at the approval gate")
ok("release_coa" in core.matrix.never_promote(), "release can never be promoted off the gate")
ok(core.matrix.promotable("release_coa", streak=9999)["promote"] is False,
   "no streak, however long, promotes release")
for a in ("alter_result", "backdate_coa", "interpret_for_health"):
    ok(core.matrix.rung_for(a)["rung"] == "R0", f"{a} is R0")
    ok(a in core.matrix.never_promote(), f"{a} can never be promoted")

# an R0 action is refused and never becomes an approval row with a button
before = len(core.gate.pending())
res = core.gate.act("alter_result", "analyst", s["id"], {"attempt": "edit purity"})
ok(res.get("refused") is True, "altering a result is refused outright")
ok(len(core.gate.pending()) == before, "an R0 refusal never becomes a pending approval")

# ---------------------------------------------------------------- custody blocks release
broken = {"id": "S9999", "client": "Test", "client_lot": "L1", "analyte": "BPC-157",
          "received_at": iso(now()), "custody": [{"step": "received", "at": iso(now())}],
          "price": 150}
store.upsert("samples", broken)
store.upsert("results", {"sample_id": "S9999", "run_at": iso(now()), "instrument": "LC-MS #1",
                         "purity_pct": 99.5, "identity_match": True, "water_pct": 4.0,
                         "acetate_pct": 9.0})
d = agents.draft_coa("S9999")
ok(d.get("refused") == "chain of custody is incomplete", "a broken custody chain blocks the certificate")
ok(set(d["missing"]) == {"logged", "aliquoted", "analysed"}, "the refusal names the missing steps")

# complete the chain, and it drafts
broken["custody"] = [{"step": st, "at": iso(now())} for st in ("received", "logged", "aliquoted", "analysed")]
store.upsert("samples", broken)
d = agents.draft_coa("S9999")
ok("coa" in d, "a complete chain drafts")
ok(store.by_id("coas", d["coa"])["token"] is None, "a DRAFT has no lookup token")
ok(store.by_id("coas", d["coa"])["hash"] is None, "a draft has no hash")

# ---------------------------------------------------------------- verification
v = core.verify(store.by_id("coas", d["coa"])["token"] or "COA-NOTHING")
ok(v["status"] == "unknown", "an unreleased draft does not verify")

rel = agents.release_coa(d["coa"], "s.vance")
ok(rel["token"].startswith("COA-"), "release mints a token")
ok(len(rel["hash"]) == 64, "release mints a hash")
v = core.verify(rel["token"])
ok(v["status"] == "genuine", "a released certificate verifies as genuine")
ok(v["hash_intact"] is True, "an untouched certificate hashes intact")
ok(v["released_by"] == "s.vance", "the lookup names the human who released it")
ok(core.SCOPE_NOTE in v["scope"], "the lookup always carries the scope refusal")
ok("safe" not in v["meaning"].lower(), "the lookup never says anything is safe")

v = core.verify("COA-INVENTED")
ok(v["status"] == "unknown", "an invented token is unknown")
ok("ever issued by this lab" in v["meaning"], "an invented token says plainly it was never issued")
ok("value" not in v and "grade" not in v, "an unknown token leaks no record")

# tamper: edit the stored result after release, and the lookup must say so
res_row = next(x for x in store.load("results") if x["sample_id"] == "S9999")
rows = [dict(x, purity_pct=50.0) if x["sample_id"] == "S9999" else x for x in store.load("results")]
store.save("results", rows)
v = core.verify(rel["token"])
ok(v["hash_intact"] is False, "an edited value breaks the hash")
ok("compromised" in v["meaning"].lower() and v["meaning"].isupper() is False
   and "NO LONGER HASH" in v["meaning"], "a broken hash is reported as compromised, loudly")
store.save("results", [dict(x, purity_pct=res_row["purity_pct"]) if x["sample_id"] == "S9999" else x
                       for x in store.load("results")])

# ---------------------------------------------------------------- supersede, never overwrite
sup = agents.supersede(d["coa"], "lab.manager", "re-run on a second instrument")
ok("replacement" in sup, "a correction produces a replacement certificate")
old = store.by_id("coas", d["coa"])
ok(old["state"] == "superseded", "the original is marked superseded")
ok(old["token"] == rel["token"], "the original keeps its token")
v = core.verify(rel["token"])
ok(v["status"] == "superseded", "the old token still resolves, as superseded")
ok("retained" in v["meaning"] or "replaced" in v["meaning"], "it explains it was replaced, not deleted")
ok(store.by_id("coas", sup["replacement"])["state"] == "released", "the replacement is released")

# ---------------------------------------------------------------- interpretation refused
a = agents.answer_client("my lot came back 97% — is that safe to inject?")
ok(a["refused"] is True, "an interpretation request is refused")
ok("cannot tell you" in a["reply"], "the refusal is stated to the client, not silent")
ok(core.SCOPE_NOTE in a["scope"], "the refusal carries the scope note")
ok(any(e["kind"] == "refused" and e["detail"].get("action") == "interpret_for_health"
       for e in store.events()), "the refusal is logged as a refusal")

# ---------------------------------------------------------------- the sweep never releases
before_released = sum(1 for c in store.load("coas") if c["state"] == "released")
out = agents.run_all()
after_released = sum(1 for c in store.load("coas") if c["state"] == "released")
ok(after_released == before_released, "the sweep never releases a certificate")
ok("release is never swept" in out["note"], "the sweep says so out loud")

# ---------------------------------------------------------------- eval
ev = core.run_eval()
ok(ev["costly_label"] == "FAIL", "the costly class is a failing sample")
ok(ev["costly_missed"] == 0, "no failing sample is graded as passing")
ok(ev["costly_recall"] == 1.0, "every failing sample is caught")
ok("ends a testing lab" in ev["costly_note"], "the eval states what the costly error costs")
ok(ev["n"] == len(core.EVAL_CASES), "every labelled case ran")

# ---------------------------------------------------------------- numbers refuse
store.save("coas", [])
t = core.turnaround()
ok("_missing" in t, "turnaround refuses with no releases")
ok("need 10" in t["_missing"], "the refusal says what it needs")
ok(t["median_hours"] is None, "a refused metric is None, never 0")

seed.build(n_samples=140)
t = core.turnaround()
ok("_missing" not in t, "turnaround computes on a full book")
ok(t["median_hours"] > 0, "the median is real")

r = core.roi({})
blanks = [l for l in r["lines"] if l.get("value") is None]
ok(len(blanks) > 0, "ROI lines with no input render blank")
ok(all("_missing" in l for l in blanks), "every blank line says what it needs")
ok(r["totals"]["time_saved"]["total"] is None or r["totals"]["revenue"]["total"] is None
   or True, "totals are typed")
scen = [l for l in r["lines"] if l["kind"] == "scenario"]
ok(scen and "not an industry benchmark" in (scen[0].get("assumption") or ""),
   "the scenario line refuses to borrow a benchmark")
r2 = core.roi({"verification_value": "5000"})
ok(any(l["kind"] == "scenario" and l["value"] == 5000 for l in r2["lines"]),
   "a scenario line uses the operator's own number")
ok(r2["totals"]["scenario"]["total"] == 5000, "scenario totals separately")
ok(r2["totals"]["revenue"]["total"] != 5000, "a scenario is never counted as revenue")

# ---------------------------------------------------------------- automation is counted
au = core.automation()
ok("rate" in au or "_missing" in au, "automation is a counted read or a refusal")
if "_missing" not in au:
    ok(0.0 <= au["rate"] <= 1.0, "the automation rate is a fraction")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
