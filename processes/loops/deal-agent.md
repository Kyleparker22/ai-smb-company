# Loop — deal-agent (David): one micro-agent per deal

> ⚠️ **NOT SCHEDULED.** There is no `yourco-deal-agent.timer` and none is sanctioned in
> `runtime/agent-registry.json`. The prompt exists and runs on demand only. Wire it via
> `.claude/skills/add-runtime-loop/` if it is ever promoted — and update this line in the same commit.

**Cadence:** on demand (intended: weekday mornings, **after** `runtime/deal_agents.py`) · **Owner:** David ·
**Output:** `nextDraft` written on escalated deals + a report · **Prompt:** `runtime/prompts/deal-agent.md` ·
**Step 0 learnings:** `learnings/sales/`

## Why
The deal reads (`ghost`, `spread`, `mirror`, `promises`) tell you *which* deals need attention. Nothing
turns that into the actual sentence you would send. This loop is the account-manager half: it takes the
escalations the deterministic engine produced and writes the human-quality draft each one is asking for.

## The two halves — order matters
1. **Deterministic first** — `runtime/deal_agents.py` stamps a fresh `agentLog` entry on every in-motion
   deal and writes `crm/_agent-escalations.json`.
2. **LLM second** — this loop reads those escalations. **Running the LLM half against a stale escalation
   file drafts for a state that has already changed**, which is worse than not drafting: the draft looks
   current and isn't.

## Method — one draft per open escalation
| Escalation | What to write |
|---|---|
| **STALE / re-engage** | A short, warm, non-salesy touch in the Founder's voice (`brand/writing-rules.md`), grounded in the actual relationship |
| **ENGAGED TODAY** | A strike-while-warm follow-up naming what they actually looked at (artifact names are in the deal's proof ledger) |
| **No draft at discovery / proposal** | The discovery ask or the proposal nudge, referencing artifacts already delivered |

Write each into that deal's `nextDraft`. CRM writes go through the repo lock and
`runtime/commit-scoped.sh` — never a bare `git add -A`.

## Guardrails
- **Never send. the Founder sends; agents draft** (CLAUDE.md). This loop writes drafts into the CRM and stops.
- **Check `graph.edges` before writing.** Many of these people are family and friends — "checking in on
  the books" to Mom reads nothing like outreach to a stranger, and getting that wrong is the kind of
  error that costs a relationship rather than a deal.
- No fabricated familiarity: reference only artifacts and events actually on the record.
