# Trip-wires — how a decision reports its own expiry

Every decision in this folder was right given what was true the day it was written. Some of
them aren't right any more, and nothing used to notice: a decision file is inert once
written, so a stance that quietly stopped matching reality kept steering the company until
somebody happened to reread it.

A **trip-wire** is an optional section that makes a decision self-reporting. The engine is
`dashboard/tripwires.py`; it evaluates every trip-wire against live OS data on each HQ poll
and surfaces the ones that have fired. Added 2026-08-07.

## The format

```markdown
## Trip-wire
- **Review:** 2026-12-01
- **Overturn if:** a proven converting funnel exists with known cost-per-qualified-lead,
  close rate and LTV, plus a few reference clients and a launched destination.
- **Check:** `signedClients >= 3 and OtherVentureCleared`
- **Check covers:** the two machine-visible preconditions only — CPL/close-rate/LTV aren't
  instrumented, so a firing check is a prompt to re-read the list, not a green light.
```

- **Review** — a date. When it passes, the decision shows as `due` on HQ. Required.
- **Overturn if** — prose. The evidence that would make this call wrong. Required, and it
  is the most valuable line: a decision whose author can't name what would refute it hasn't
  finished being made.
- **Check** — optional. A machine test over live OS facts. Write `_none — <why>_` when the
  condition genuinely isn't measurable; that is a documented absence, not a gap, and the
  engine treats it as prose rather than reporting a parse error.
- **Check covers** — write this whenever the check is a *partial* proxy for the prose. A
  check that covers half the condition and doesn't say so is the failure mode here: it
  turns a nuanced revisit trigger into a green light.

## The check language

Deliberately tiny. Only `<fact> <op> <number>`, a bare boolean fact, or `not <fact>`, joined
by **all-`and`** or **all-`or`**. Mixing `and` with `or` is **refused**, not guessed — a
trip-wire that reads ambiguously must not fire ambiguously; split it into two decisions'
worth of thinking, or into prose.

There is no `eval()`. Decision files are text that agents and collaborators edit; running
arbitrary code out of them would make every markdown file an execution path.

**Facts available** (all computed live; run `python3 dashboard/tripwires.py` to print current values):

| Group | Facts |
|---|---|
| Commercial | `mrr` `liveClients` `signedClients` `dealsInMotion` `prospects` `pipelineValue` `referredMRR` `activeConnectors` `activeAdvisors` `crmNonFounderUsers` |
| System | `loopsBuilt` `loopsStale` `loopsNever` `commits7d` |
| Gates | `counselGatesCleared` `counselGatesTotal` `counselGatesBlocked` `OtherVentureCleared` |
| Trust | `trustActions` `trustIncidents` `drillsUndetected` |
| Per-decision | `daysSinceDecision` |

Commercial facts come from `server.goals_currents()` — the same computation the HQ goal band
uses — so a trip-wire can never disagree with the dashboard about what MRR is.

## Verdicts

| Verdict | Meaning |
|---|---|
| `contradicted` | the check fired — live data now satisfies the overturn condition |
| `due` | the review date has passed |
| `watching` | a trip-wire exists, nothing has fired |
| `uncovered` | no trip-wire |
| `unreviewed` | uncovered **and** older than 180 days — nobody has looked in months |

A check that can't be evaluated (unknown fact, unparseable term) is reported as an **error**,
never silently read as "did not fire". Silence has to mean something.

## Who writes them, and why coverage is deliberately partial

A trip-wire encodes *when one of the Founder's strategic calls dies.* That is the Founder's judgment, not
an agent's. The seeded set **transcribes** revisit conditions the decision files already
state in their own words; where a file never stated one, it is left `uncovered` on purpose
and shows up in the coverage count. **The coverage number is a to-do list, not a defect** —
the honest move is for the Founder (or the decision's owner) to add the missing ones, not for an
agent to invent conditions nobody agreed to.

## When writing a new decision

`.claude/skills/log-decision/` includes the trip-wire section in the house format. Fill it
in at authoring time — the moment you're most able to say what would change your mind is
the moment you're deciding.
