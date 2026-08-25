#!/usr/bin/env python3
"""Immune drill executor — `silent-schema-drift`, run for real, against nothing live.

NAMING, so the two "immune" ideas don't collide: `runtime/immune/` is the CROSS-CLIENT
immune system — real incidents at one client, anonymized and propagated as vaccinations
under a permanent human gate. This directory is the other half: **deliberately induced**
faults against yourco's own OS, to find out whether it would notice. One learns from
incidents that happened; the other manufactures them on purpose. They are complementary.

THE HYPOTHESIS UNDER TEST
  When the CRM's shape changes underneath them, HQ's consumers degrade to an explicit
  gap ("—", null, a stated note) and never to a confident wrong number.

WHY THIS DRILL IS SAFE TO AUTOMATE (the others aren't, and stay operator-placed)
  It never touches crm/data.json. It builds mutated COPIES in a temp dir and points the
  consumers at them by monkeypatching their module-level path constant for the duration
  of the check. Nothing is written to the repo except the drill's own ledger rows.

MUTATIONS
  1. stage-rename      "live" -> "l1ve"          — a renamed enum, the classic silent break
  2. blanked-money     retainer/value -> null    — the field exists but carries nothing
  3. amputated-deals   deals: []                 — a whole collection disappears
  4. wrong-type        retainer -> "1,000"       — a string where a number is expected

PASS/FAIL, per mutation
  PASS  = no exception, AND every metric whose input is now absent reads 0/None,
          AND marginPct stays None (it must never render a flattering 100%).
  FAIL  = a crash, or any metric that keeps a plausible non-zero value it can no
          longer justify from the mutated input.

Run:  python3 runtime/drills/schema_drift.py            # execute + record to the drill ledger
      python3 runtime/drills/schema_drift.py --dry-run  # execute, print, record nothing
"""
import os, sys, json, copy, shutil, tempfile, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
RUNTIME = os.path.dirname(HERE)
ROOT = os.path.dirname(RUNTIME)
sys.path.insert(0, RUNTIME)
sys.path.insert(0, os.path.join(ROOT, "dashboard"))

DRILL_ID = "silent-schema-drift"


def _load_crm():
    with open(os.path.join(ROOT, "crm", "data.json"), encoding="utf-8") as f:
        return json.load(f)


def _mutations(crm):
    """Each mutation returns (name, mutated_doc, expectation) where expectation names the
    metrics that MUST collapse. Anything else surviving unchanged is fine — the drill
    checks for fabrication, not for maximal breakage."""
    out = []

    m = copy.deepcopy(crm)
    for d in m.get("deals", []):
        if d.get("stage") == "live":
            d["stage"] = "l1ve"
    out.append(("stage-rename", m, ["mrr", "liveClients", "referredMRR"]))

    m = copy.deepcopy(crm)
    for d in m.get("deals", []):
        d["retainer"] = None
        d["value"] = None
        d["buildFee"] = None
    out.append(("blanked-money", m, ["mrr", "referredMRR"]))

    m = copy.deepcopy(crm)
    m["deals"] = []
    out.append(("amputated-deals", m, ["mrr", "liveClients", "dealsInMotion", "newProspects",
                                       "referredMRR"]))

    m = copy.deepcopy(crm)
    for d in m.get("deals", []):
        d["retainer"] = "1,000"   # a string that LOOKS like money
        d["value"] = "twelve k"
    out.append(("wrong-type", m, ["mrr", "referredMRR"]))

    return out


def _check(server, path, expect_zero):
    """Point the consumer at the mutated copy and read its metrics back."""
    original = server.CRM
    server.CRM = path
    try:
        cur = server.goals_currents()
        pipe = server.pipeline_summary()
    finally:
        server.CRM = original

    problems = []
    for k in expect_zero:
        v = cur.get(k)
        if v not in (0, None):
            problems.append(f"{k} kept a value ({v!r}) its mutated input can no longer justify")
    if cur.get("marginPct") is not None:
        problems.append("marginPct rendered a number with no cost feed — it must stay null")
    if pipe is None:
        problems.append("pipeline_summary returned None instead of an honest empty summary")
    return problems, {"mrr": cur.get("mrr"), "liveClients": cur.get("liveClients"),
                      "dealsInMotion": cur.get("dealsInMotion"),
                      "marginPct": cur.get("marginPct"),
                      "pipelineValue": (pipe or {}).get("value")}


def run(dry_run=False):
    import server  # the real consumer under test

    crm = _load_crm()
    tmp = tempfile.mkdtemp(prefix="yourco-drill-")
    results = []
    try:
        for name, doc, expect in _mutations(crm):
            p = os.path.join(tmp, f"{name}.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(doc, f)
            try:
                problems, observed = _check(server, p, expect)
            except Exception as e:  # a crash IS a failure — an OS that dies on bad data
                problems, observed = [f"raised {type(e).__name__}: {e}"], {}
            results.append({"mutation": name, "passed": not problems,
                            "problems": problems, "observed": observed})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = all(r["passed"] for r in results)
    print(f"IMMUNE DRILL — {DRILL_ID}  ({len(results)} mutations, live data untouched)\n")
    for r in results:
        print(f"  {'PASS' if r['passed'] else 'FAIL'}  {r['mutation']:<18} {r['observed']}")
        for p in r["problems"]:
            print(f"        ! {p}")
    print(f"\n  verdict: {'DETECTED — every mutation degraded honestly' if passed else 'MISSED — a consumer fabricated through a broken input'}")

    if dry_run:
        print("\n  --dry-run: nothing recorded to the drill ledger")
        return passed, results

    import trust_ledger as TL
    armed = TL.arm_drill(DRILL_ID, placed_at="temp copies of crm/data.json (live file untouched)",
                         note=f"automated executor: {len(results)} mutations "
                              f"({', '.join(r['mutation'] for r in results)})")
    TL.detect_drill(
        DRILL_ID, by="dashboard consumers (goals_currents + pipeline_summary)",
        detected=passed,
        note=("every mutation degraded to 0/None with no fabricated value"
              if passed else
              "; ".join(f"{r['mutation']}: {'; '.join(r['problems'])}"
                        for r in results if not r["passed"])[:900]))
    print(f"\n  recorded to loops/_trust/drills.jsonl (run #{armed['seq']})")
    return passed, results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ok, _ = run(ap.parse_args().dry_run)
    sys.exit(0 if ok else 1)
