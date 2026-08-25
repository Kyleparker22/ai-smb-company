# /agents/

The internal agents' workspaces — one folder per yourco agent (roster + roles: `04_agent_roster.md`). **Moved out of `clients/` 2026-08-07** per the Founder: `clients/` holds clients only.

Notable contents:
- `webb/pages/` — the staged yourco site (yourco-site-v2; served via launch.json `yourco-webb-pages` :8793)
- `Reed/` — video/visual production: `02_build.md` (production standard v3), `productions/` (per-asset ledgers), `demos/` (e.g. salon-voice-agent :8797)
- `reilly/`, `michelle/` — outbound machine + copy
- others — each agent's docs, loops output staging, and working files

## The roster is the spec; this folder is the workspace

**`04_agent_roster.md` is authoritative** for every agent's role, trigger, scope, approval gate and
status — one row each, all 27, one place. These folders hold what is *local* to an agent: its lineage,
its working notes, its eval set, its artifacts.

That split is now enforced rather than hoped for. Every `_README.md` opens with a block pointing at the
roster and **deliberately not copying it** — because a copied fact drifts, which is exactly what
happened here: scope appeared in 5 of 27 READMEs, trigger and gates in about a third, all of them
partial restatements of a table that already had the answer.

## Can these agents learn? (measured 2026-08-23 — read this before assuming)

Three different things could mean "the agent improves," and only one of them actually moves.

| Layer | Status |
|---|---|
| **How it runs** — operational patterns | ✅ **Works.** 53 entries in `learnings/`, read at Step 0 by every loop, trigger-scoped since 2026-08-13. An agent that errs writes a learning; the next run reads it and adjusts. |
| **What it knows** — domain currency | ⚠️ **One agent, company-wide.** `source-watch`, `brett-ideas` and the monthly `advisor` memo are **all Brett's**. Kolby does not watch eval practice; Polo does not watch pricing thinking; Michelle does not watch outbound copy. |
| **Who it mirrors** — Lineage | 🔴 **Frozen.** 26 of 27 name a real authority (Bird → Jason Lemkin, Kolby → Hamel Husain). **Nothing has ever re-examined one.** If that authority's thinking moved, or a better one emerged, no part of this OS would notice. |

Agent docs are also only ever edited by a human in a commit — **no loop writes to an agent's own docs.**
Kolby's and Mario's have had no content change since June; their August commits were the folder move.

So the honest answer to *"are the agents locked into their context?"* is: **they learn how to run, they
do not learn what to know.** Every `_README.md` now carries a **Stays current:** line saying so in its
own case, so the gap is visible 27 times instead of zero.

## Two shapes, both valid — know which you are looking at

There is no single standard here, and pretending otherwise makes eight folders look broken when they
are not. Measured 2026-08-23:

| Shape | Who | What it looks like |
|---|---|---|
| **Doc-first** (19 agents) | mostly the dormant / trigger-gated ones | `_README.md` + `01_discovery.md` + `02_build.md` + `03_eval.md` — 200–570 lines describing what the agent *would* do |
| **Prompt-first** (8 agents) | mostly the busiest live ones — Kolby, Jim, Sadie, David, Melanie, Rafi, Ray, Pickle | `_README.md` only; the behaviour that actually runs lives in `runtime/prompts/<loop>.md` |

⚠️ **Documentation is inversely correlated with activity.** Kemba has 522 lines and runs zero loops;
Kolby has 57 lines and runs four. That is not simply a gap to fill — the 01/02/03 trio is inherited
from the *client* template (`clients/_yourco-template/`), where discovery→build→eval describes work not
yet done. For an internal agent already running every morning, the executable prompt is the more honest
artifact: it cannot drift from behaviour, because it *is* the behaviour.

**The rule:** an agent that runs a loop must have its behaviour in the loop prompt, and that prompt must
name it (`> **Owner:** <Agent>`, enforced by `runtime/consistency-check.py`). The 01/02/03 trio is
optional for those — write it when there is something to say that the prompt cannot carry. Do not
back-fill it for ceremony.

Conventions:
- Agent names are **internal-only** — never on external or client-facing surfaces.
- Runtime loop *outputs* still land in `/loops/` (dated artifacts); these folders are the agents' durable working state.
- Historical paths: anything written before 2026-08-07 (loops/ artifacts, `_archive/`, daily logs) may still say `clients/<agent>` — those are point-in-time records, left as written.
