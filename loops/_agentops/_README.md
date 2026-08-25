# `_agentops/` — the agent-substrate evidence stores

Four append-only JSONL stores written through `runtime/ledger.py` (monotonic `seq`, corrections as new events, corruption counted rather than swallowed). Added 2026-08-13 — decision: `decisions/2026-08-13_agent-substrate-upgrade.md`.

| Store | Written by | Read by | What it answers |
|---|---|---|---|
| `runs.jsonl` | `runtime/run-loop.sh` → `runtime/run_journal.py --record`, plus `--checkpoint` | `run_journal.py --status/--resume`, `agent_payroll.py` | What did this run cost, and what did the last one finish before it died? |
| `failures.jsonl` | loops hitting an anti-spin stop (`runtime/failure_traces.py --record`) | `failure_traces.py --propose` at the weekly eval-review | Which *instruction* keeps producing the same failure? |
| `reviews.jsonl` | `runtime/second_opinion.py` | the R1.5 rung | Who gave the second opinion, through which lens, and what did they find? |
| `approvals.jsonl` | `runtime/decaying_approval.py` | the sweep + `--evidence` | What did the Founder's silence actually decide, and did it come out clean? |

`provenance.jsonl` also lands here when `runtime/provenance.py` records a wrap or a policy check.

## All four start empty, and that is correct
Nothing can be backfilled. Per-run cost previously went to `loops/_runtime/<loop>.log`, which is **gitignored and host-local**, so the history is gone; the other three stores did not exist before there was a mechanism to write them. Every reader is built to say `unpriced` / `insufficient-evidence` / `no traces yet` rather than show a zero — a fabricated zero in a cost or trust column is the number nobody thinks to question.

## The rule that governs all of them
**An evidence store never ships seeded fakes.** Test rows written while building these were deleted before commit. If you need sample data, write it to a temp path — `runtime/test_agentops.py` does exactly that.
