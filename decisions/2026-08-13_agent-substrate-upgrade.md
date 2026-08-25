# 2026-08-13 — The agent-substrate upgrade: eleven changes to how yourco's agents remember, cost, prove and decide

**Decision owner:** the Founder. **Built:** 2026-08-13. **Trigger:** an external scan of what the best agent builders and agent companies actually ship (Sierra, Cognition/Devin, Anthropic Agent Skills, LangGraph, the CaMeL/FIDES line, ServiceNow/Workday/Atomicwork agent-workforce platforms, AG-UI/A2UI), read against yourco's own OS.

## The finding that drove it
On **organization, autonomy, governance and self-instrumentation, yourco is at or ahead of what those platforms ship.** Where it was behind was narrower and entirely technical — and invisible to any buyer:

- memory retrieved by **folder** rather than by **trigger**, so cross-cutting learnings never reached the runs that needed them;
- runs with good *stop* rules and no *resume* story, so a correct stop at minute 14 started from zero next firing;
- **per-loop cost generated ~20×/day and thrown away** into a gitignored host-local log;
- a capability deny-list with **no provenance**, so inbound content entered context in the same shape as yourco's own instructions;
- the anti-spin stop signal — the exact input the self-improving-agent literature runs on — dying as prose in artifacts;
- the streak rule unable to distinguish **reliable** from **lucky**;
- every escalation path terminating at one person;
- rejected ideas leaving no trace, so the same proposals returned with no evidence.

## What was decided and built
Five patterns **copied** from the scan, six **built** from it. All eleven land as code with tests, not as intentions.

| # | Change | Where |
|---|---|---|
| 1 | **Triggers on learnings** — retrieval by trigger, with the domain+recency read kept as a floor. 42/42 entries backfilled. | `runtime/learning_triggers.py`, `learnings/_README.md` |
| 2 | **The anti-library** — rejected ideas with revisit conditions, in the *existing* trip-wire grammar; idea loops must clear it before proposing. | `rejections/`, `runtime/rejections.py` |
| 3 | **Run journal** — checkpoints, hand-off on the next firing, and per-run cost captured from `claude -p --output-format json`. | `runtime/run_journal.py`, `run-loop.sh` |
| 4 | **Provenance-typed context** — untrusted content fenced as data; a deterministic trust × action-class policy; an injection scanner that labels and never strips. | `runtime/provenance.py` |
| 5 | **Failure traces → skill patches** — anti-spin stops become structured traces; recurrences become a proposed diff against the *file whose instruction was in force*. | `runtime/failure_traces.py` |
| 6 | **Agent payroll** — per-agent cost and the eighth governance dimension, budget. | `runtime/agent_payroll.py`, registry §`agent_budgets` |
| 7 | **R1.5** — a second opinion between the agent and the Founder. | `runtime/second_opinion.py`, `processes/autonomy-matrix.md` |
| 8 | **Calibration-gated autonomy** — promotion needs the streak **and** evidence the agent knows when it's unsure. | `runtime/agent_calibration.py` |
| 9 | **Decaying approvals + silence as evidence** — inside a hard three-part eligibility boundary. | `runtime/decaying_approval.py` |
| 10 | **The trace definition** — six fixed checkpoint kinds; the observability definition without the observability platform. | `runtime/run_journal.py` |
| 11 | **75 honesty assertions** pinning every refusal above. | `runtime/test_agentops.py` |

## What was deliberately NOT done
- **Outcome-based pricing** (Sierra's model). Needs a countable resolution event and volume; at n=0 clients it is a way to do free work.
- **A2A protocol.** A watch item, not a build. The trigger to care is a client OS needing to talk to a *vendor's* agent.
- **An observability platform.** Took the definition, skipped the tooling — 20 loops do not justify a trace backend.
- **Open-ended generative UI.** One narrow application (the per-decision approval surface) shipped; the general pattern did not, because the external visual bar is "$50k-agency" and open-ended GenUI is how you get generic.

## Three claims this decision explicitly does NOT make
1. **This is not CaMeL.** CaMeL needs an interpreter mediating every tool call; yourco does not own that layer. What shipped is an envelope, a deterministic policy table, an audit trail and a scanner. The load-bearing control remains the harness deny-list. Anything stronger on an external surface would be a fake control.
2. **A budget cap does not enforce.** It fires on the next read and cannot stop a run in flight. Real enforcement needs a pre-flight check inside `run-loop.sh`.
3. **R1.5 does not catch a shared wrong premise.** Two reads of the same model correlate. It catches completeness, policy, consistency, provenance and arithmetic — and that limit is printed on every verdict it issues.

## Everything starts empty, on purpose
Four of the new stores have zero rows and cannot be backfilled. Every reader says `unpriced` / `insufficient-evidence` / `no traces yet` instead of showing a zero. **The first honest read of this work is available ~30 days after the runtime picks up the new `run-loop.sh`** — before that, the correct verdict on most of it is "wired, unproven."

## Trip-wire
- **Review:** 2026-11-13
- **Overturn if:** 30+ days of run-journal data show the substrate is not being used — loops are not recording failure traces when they stop, not checking the anti-library before proposing, and per-agent cost is still dominated by an unattributed remainder. That would mean the wiring was written into the contract but is not being honoured, and the answer is fewer mechanisms, not more.
- **Check:** `daysSinceDecision >= 30 and loopsStale >= 20`
- **Check covers:** a weak proxy only, and deliberately time-fenced. `loopsStale` was **already 14 on the day this was written**, so a bare `loopsStale >= 14` check fired as `contradicted` within an hour of the decision existing — before the 30 days of data its own prose depends on could possibly exist. The `daysSinceDecision` term stops a trip-wire from contradicting a decision that has not yet had time to be wrong. Even then it only detects the runtime going quiet, which would starve every store here; it cannot see the actual failure mode — loops running fine while ignoring the new steps. That is visible only by reading `loops/_agentops/*.jsonl` for rows and running `python3 runtime/learning_triggers.py --check` for coverage. Treat a firing check as "go read the stores", never as the verdict itself.
