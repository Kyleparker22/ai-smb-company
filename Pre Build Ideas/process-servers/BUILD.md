# Serve OS — process serving agencies (build 57)

**Working name:** Serve OS · **Launch:** `prebuild-serve-os` · **Port:** 8877
**Synthetic operator:** "Docket Process Service" — 6 servers, ~300 open serves for law firms
across 3 counties.

## Why this industry (the overlooked test)
Process serving is pure paperwork-with-consequences and utterly untargeted by AI vendors. The
product IS the paper: a defensible affidavit of service. A bad one collapses a case, triggers a
sanctions motion, and ends the law-firm relationship that feeds the agency.

## The bleeding neck
The affidavit. It attests, under penalty of perjury, what a human server personally did — and
software must never write facts into it that the server didn't record, never sign it, and never
attest. The quiet leaks: attempt logs reconstructed from memory a week later (indefensible),
jurisdiction-specific due-diligence counts (how many attempts, what hours, before substituted
service is allowed) re-derived per serve, court deadlines missed, and law-firm status asks
answered "let me check with the server."

## Modules
1. **Serve pipeline** (Operations) — papers in → attempts → served / substituted / non-est, with
   the court's deadline as the master clock; the board ranks by days-to-deadline.
2. **The attempt log** (Operations) — append-only, recorded AT the attempt (time, address, GPS
   ref, what happened, who answered); a late-recorded attempt is labeled late-recorded forever;
   `edit_attempt` does not exist — corrections are new entries.
3. **The affidavit rule** (Operations) — drafts assemble ONLY from recorded attempts, verbatim;
   `sign_or_attest` R0 — the server reviews, corrects (as new records), and signs; substituted
   service drafts refuse until the recorded jurisdiction's due-diligence rule (n attempts,
   spread across recorded hour-bands) is satisfied by the log itself.
4. **Client desk** (Customer) — the law firm's status ask answered from the record (attempts,
   next attempt window); deadline-risk flagged to a human early; nothing speculative.
5. **Assignment & routing** (Back Office) — serves assigned by territory and deadline pressure;
   a server's day list ordered by court clock, not drive whim.

## Guardrails (load-bearing)
- `sign_or_attest` — **R0, never-promote.** The affidavit is a human's oath.
- `add_unrecorded_fact_to_affidavit` — **R0, structural**: drafts read only the attempt log.
- `edit_attempt` — does not exist; append-only, tested via hasattr.
- `declare_due_diligence_met` — only the recorded rule + the log itself; refused with the gap
  named otherwise. Outward drafts R1.

## ROI (typed)
Serves/server-day throughput (counted, operator lift) · rush-serve capture (counted) · the
quashed-service file (scenario, never a number) · status-call hours returned (time_saved).

## Demo path
Deadline board → attempt logged live → affidavit drafted verbatim-from-log → substituted-service
refused at 2 of 3 attempts → law-firm status ask answered from record → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the deadline-risk / evasion
message from the law firm.
