# /loops/

> ⚠️ **NOT YOURS YET.** Each folder keeps **one labelled example artifact** so you can see what that loop produces.
They describe someone else's business. Your own runs overwrite this the first time a timer
fires.


Every recurring process writes one dated artifact per run, and the next run reads it. That is the
closed loop: an artifact the machine produced and the machine re-reads.

**This page was rewritten 2026-08-24.** It had said *"outputs of the four recurring closed loops"* and
listed four subfolders. There are 42<!--#count: dirs loops/*-->. It described a world that stopped being
true around the time the runtime went always-on, which is the failure this repo keeps having: the
content was right and the index in front of it was months stale.

## Two kinds of folder here, and they are not the same thing

The distinction is the leading underscore, and nothing had ever written it down:

- **`_underscore/` — 17<!--#count: dirs loops/_*--> STORES.** Written by a *tool* when it runs, not by a scheduled loop.
  `_consistency` is the invariant checker's report, `_coach` is practice records, `_trust` the ledger,
  `_health` the runtime's own pulse — where the **missing** lines are the measurement.
  Some are append-only JSONL rather than dated markdown. **No prompt file exists for these.**
- **plain-name/ — 27 LOOP OUTPUTS.** One folder per scheduled loop, most paired with
  `runtime/prompts/<name>.md` — the SOP is the method, the prompt is what actually runs, this is what
  came out.

## Stores

| folder | files | newest |
|---|---|---|
| `_advisory/` | 6 | 2026-08-13_site-visual-direction |
| `_agentops/` | 2 | never fired |
| `_anthropic/` | 11 | 2026-08-24.json |
| `_audit/` | 14 | 2026-08-16_tools-and-costs-review |
| `_build-journal/` | 2 | never fired |
| `_coach/` | 1 | never fired |
| `_consistency/` | 16 | 2026-08-24 |
| `_crm-hygiene/` | 28 | 2026-08-24 |
| `_governance/` | 13 | 2026-08-24 |
| `_hq/` | 2 | never fired |
| `_inbox/` | 1 | 2026-08-24 |
| `_instantly/` | 11 | 2026-08-24.json |
| `_pregolive/` | 2 | 2026-08-16 |
| `_runtime/` | 0 | never fired |
| `_triage/` | 1 | 2026-08-24_batch-ten |
| `_trust/` | 2 | never fired |
| `_watchdog/` | 25 | 2026-08-16 |

## Loop outputs

| folder | files | newest |
|---|---|---|
| `advisor/` | 9 | 2026-08-03 |
| `aeo-geo/` | 4 | 2026-07-07 |
| `brand-audit/` | 3 | 2026-08 |
| `brett-ideas/` | 7 | 2026-08-21_ideas |
| `connector-spotter/` | 1 | never fired |
| `content/` | 15 | 2026-08-21 |
| `crm-autolog/` | 13 | 2026-08-21 |
| `customer-health/` | 11 | 2026-08-19 |
| `end-of-day/` | 2 | 2026-06-11 |
| `eval-review/` | 6 | 2026-07-12 |
| `finance/` | 12 | 2026-08-17 |
| `gap-audit/` | 2 | 2026-08-07 |
| `granola-crm-sync/` | 3 | 2026-08-11 |
| `inbox-signal/` | 1 | never fired |
| `inbox-triage/` | 31 | 2026-08-21 |
| `initiative/` | 12 | 2026-08-21 |
| `lineage-review/` | 1 | never fired |
| `melanie/` | 1 | 2026-06-11 |
| `melanie-briefing/` | 10 | 2026-08-21 |
| `monday-briefing/` | 11 | 2026-08-17 |
| `open-loops/` | 19 | 2026-08-21 |
| `outreach-eval/` | 1 | never fired |
| `pipeline-report/` | 6 | 2026-07-13 |
| `pricing-review/` | 2 | 2026-Q3 |
| `sadie/` | 30 | 2026-08-21_intent-sweep |
| `sales/` | 11 | 2026-08-17 |
| `source-watch/` | 4 | 2026-08-21 |

## What this index will not pretend

- **`_runtime/` is NOT empty — it is one of the busiest directories here.** It holds every loop's run
  log (`run-loop.sh` writes `loops/_runtime/<loop>.log`) and is **gitignored and host-local**, so it
  reads as empty on a laptop and is full on the VPS. An earlier version of this page called it "never
  written," which was simply wrong: `.gitignore:11` and `runtime/run-loop.sh:40` both name it, and
  `processes/loops/watchdog.md` reads it. **Do not delete it.**
- **Two folders were archived 2026-08-25** to `_archive/`, each with a note saying why: `end-of-day/`
  (superseded by `daily-logs/`; never in the agent registry) and `melanie/` (an orphan from before her
  loops were named). ⚠️ **Archiving `melanie/` says nothing about Melanie** — she runs two live loops,
  `melanie-briefing/` (07:45 ET) and `initiative/` (08:45 ET), and is the conductor. A dead folder
  wearing an active agent's name is exactly what invites the wrong conclusion.
- **Several folders have a prompt and no artifact** — `connector-spotter`, `inbox-signal`,
  `lineage-review`, `outreach-eval`. Those loops are armed and have not fired, which is a true state
  and not a fault.
- A newest date here is **when a file was last written**, not proof the loop is healthy. Liveness is
  the watchdog's job (`loops/_watchdog/`), and `runtime/agent-registry.json` is the canonical list of
  what is *sanctioned* to run — not this page.

## Convention

One dated artifact per run, `YYYY-MM-DD.md` (monthly and quarterly loops use `YYYY-MM` and `YYYY-Qn`).
**Artifacts are runtime-owned**: on a conflict, prefer the runtime's copy. Never rewrite a past
artifact to make it agree with today — a dated record was true when it was written.
