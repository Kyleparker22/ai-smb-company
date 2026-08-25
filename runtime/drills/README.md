# runtime/drills — deliberately induced faults, and whether the OS noticed

**Two "immune" ideas live in this repo. They are not the same thing, and the names have to stay
straight:**

- `runtime/immune/` — the **cross-client** immune system. Real incidents at one client, screened
  and anonymized, published as vaccinations every other client OS absorbs. Learns from what
  *happened*. Permanently human-gated.
- `runtime/drills/` — **this** one. Faults yourco induces on purpose against its own OS, to find
  out whether it would notice. Manufactures what *hasn't* happened yet.

They're complements: one propagates the lesson from a real failure, the other goes looking for
failures nobody has had yet.

## Why it exists

The moat claim is "reliability, eval, observability, approval — the layer no-code can't build."
Watchdogs and eval reviews measure the OS while it's behaving. Neither answers the question a
serious buyer eventually asks: *what happens when something breaks, and would you know?* An
untested detector is a belief, not a control. A drill converts the belief into a record.

## The rules

1. **Every drill is inert.** The payload is a canary — a harmless, detectable string or an
   absence. No drill ever causes a real send, delete, payment, or client-visible action, even
   if the OS fails it completely.
2. **Nothing live is touched.** Drills operate on temp copies, scratch branches, or local
   instances. A drill that requires editing a live credential or a live data file is written so
   the operator does it on a copy — see each catalog entry's `place` field.
3. **Operator-placed by default.** Only `schema_drift.py` is automated, because it provably
   cannot touch anything real. An autonomous fault-injector wired into live systems is exactly
   the day-one high-blast-radius autonomy `processes/autonomy-matrix.md` says not to build.
4. **Silence is a miss.** A drill past its detection window with no verdict scores UNDETECTED,
   never "pending". Not noticing is the failure being tested for.
5. **A rate needs a sample.** One detected drill is reported as "1 of 1", not "100%".

## The catalog

Defined in `runtime/trust_ledger.py` (`DRILLS`) so the catalog and the scoring can't drift apart.
Six entries today: stale source · broken connector · canary injection (prompt injection) ·
contradictory instruction · silent schema drift · unauthorized scope.

```bash
python3 runtime/trust_ledger.py --drills            # the catalog
python3 runtime/trust_ledger.py --plan <drill-id>   # exactly what would be placed; places nothing
python3 runtime/trust_ledger.py --arm <drill-id>    # record that you placed it; starts the clock
python3 runtime/trust_ledger.py --detect <drill-id> --by "<the control that caught it>"
python3 runtime/trust_ledger.py --detect <drill-id> --missed
python3 runtime/trust_ledger.py --sweep             # expire overdue runs to UNDETECTED
```

## The automated one

```bash
python3 runtime/drills/schema_drift.py --dry-run   # run it, print, record nothing
python3 runtime/drills/schema_drift.py             # run it and record the verdict
```

Four mutations of a **copy** of `crm/data.json` — renamed stage enum, blanked money fields, an
amputated collection, and a string where a number belongs — pushed through the real dashboard
consumers. PASS means every metric whose input disappeared collapsed to 0/None and `marginPct`
stayed null. FAIL means a consumer kept a plausible number it could no longer justify.

## Results

Land in `loops/_trust/drills.jsonl` (append-only) and render on **HQ → Evidence → Immune drills**.
The weekly `evidence-sweep` loop (Kolby, Sun 16:30 ET) runs the automated drill, sweeps overdue
runs, and reports which catalog entries have never been armed — that last list is the honest
measure of coverage.

**Owners:** Kolby (runs + scores) · Rafi (drill design for anything touching isolation or PII) ·
the Founder (approves any new drill class that isn't obviously inert).
