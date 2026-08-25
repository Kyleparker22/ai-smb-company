---
name: log-decision
description: Write a decision-log entry in the house format. Use whenever a settled call is made — scope, pricing, ICP, stack, moat-touching, template upgrades, anything future-the Founder would ask "wait, why did we decide X?"
---

# log-decision

## Canonical doc
`decisions/_README.md`.

## Steps
1. File: `decisions/YYYY-MM-DD_<short-slug>.md` — one decision per file.
2. Sections, in order:
   - **Decision** — what was decided, one sentence
   - **Context** — what prompted it
   - **Options considered** — alternatives, briefly
   - **Why** — the reasoning that won
   - **Reversibility** — what would need to be true to revisit
   - **Trip-wire** — the machine-checked version of Reversibility. Format + the live fact list: `decisions/_TRIPWIRES.md`
3. Write the trip-wire **at authoring time**. The moment you are most able to say what would change your mind is the moment you are deciding; nobody reconstructs it well six months later. Minimum:
   ```markdown
   ## Trip-wire
   - **Review:** YYYY-MM-DD
   - **Overturn if:** <the evidence that would make this call wrong>
   - **Check:** `signedClients >= 3 and OtherVentureCleared`   ← or `_none — <why>_`
   ```
   `dashboard/tripwires.py` evaluates every `Check` against live OS data on each HQ poll and flags the decision on **HQ → Evidence** the moment its own stated condition fires. Rules that matter: `_none — <why>_` is a valid, documented absence; mixing `and` with `or` is refused rather than guessed; and if the check only covers *part* of the prose, add a **Check covers:** line saying so — a half-covering check that doesn't admit it turns a nuanced revisit trigger into a green light.
4. **If the decision locks a domain in the partner review→lock run** (`processes/partner-b-walkthrough-schedule.md`, 8/11–8/26), add a `**Locks:** <domain>` line naming the domain exactly as that calendar spells it — several allowed, comma-separated. HQ → **Partners** reads that marker to mark the domain locked; without it the domain shows as *likely — unconfirmed*.
5. If the decision changes yourco's positioning, model, or moat: **edit `CLAUDE.md` first** (it's the always-loaded boot context) and link the decision file from it.
6. Update any doc the decision supersedes — mark the old one or `git mv` it to `_archive/`. A decision that contradicts a live doc without touching it creates drift the next agent inherits.

## Gotchas
- Decisions are **settled** calls. Observed patterns → `learnings/` (see `write-learning`); procedures → a skill (see `create-skill`).
- Especially log anything pulling toward parked directions (self-serve SaaS) — that's the drift the log exists to catch.
- Counsel-gated or securities-gated items: mark the gate in the decision itself (the referral/equity entries are the pattern).
