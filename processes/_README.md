# /processes/

SOPs beyond the core delivery loop (which is `/02_delivery_loop.md`). **147 files**, most of them
in the six subfolders below.

> **The counts on this page are machine-checked** (`runtime/consistency-check.py`) — they were hand-typed
> when this page was rewritten on 2026-08-23 and were wrong four days later: 134 files had become 172,
> and `partnerships/` had **doubled** from 33 to 66. A page whose only job is telling you what
> is here should not be the thing that goes stale.

## What's in here

| Path | Files | What it holds |
|---|---|---|
| `loops/` | 31 | **One SOP per recurring loop.** Pairs with `runtime/prompts/<loop>.md` — the SOP is the method, the prompt is what actually executes. |
| `partnerships/` | 33 | The connector program: packet, rate card, target list, enablement, and the connector console. |
| `advisor-training/` | 7 | **The advisor curriculum (2026-08-24).** Six lessons on the full-time sales role — the job's authority limits, lead-high-land-anywhere, the AI-OS formula, running the audit call, scoping by pillar, and objections. Plus `_drills.json`, the practice scenarios `crm/coach.py` serves. n=0 advisors hired: this is the spine, not a finished course. |
| `outbound/` | 11 | The proof-led outbound engine — sequence copy, warm-network pass, campaign kits. |
| `contracts/` | 10 | Legal templates. Counsel-gated; check `counsel-gates.md` before using one. |
| `local-media/` · `content/` | 7 | Local-media plays and the content engine. |
| *(root)* | 44 | Everything else — one SOP per file. |

## The loop pairing rule

Every recurring loop should have **two** files, and they do different jobs:

- `processes/loops/<name>.md` — the **method**: what the loop does, its inputs, its output shape
- `runtime/prompts/<name>.md` — the **executable**: what the runtime actually feeds the model, carrying
  `> **Owner:** <Agent>` and its Step 0 learnings domain

Most prompts open with *"follow `processes/loops/<name>.md` exactly"*, which is what keeps the two in step.

**No prompt is currently unpaired.** `deal-agent`, `evidence-sweep`, `melanie-briefing` and
`outreach-eval` were the four prompt-first exceptions this page used to name — all four were given SOPs on
2026-08-23, the same day this page was written to explain their absence. The matching allow-list in
`runtime/consistency-check.py` was emptied 2026-08-24 and kept (rather than deleted) for the next genuine
exception. Prompt-first remains a valid shape (`agents/_README.md` §"Two shapes"); nothing is in it today.

**Four SOPs deliberately have no prompt**, each for a stated reason:

| SOP | Why no prompt |
|---|---|
| `client-error-sweep` | Activation-gated — fires at a client go-live, and there are none yet |
| `granola-crm-sync` | Runs as a Cowork scheduled task on the Founder's Mac, not a VPS loop |
| `session-friction-audit` | Mac-local via the scheduled-tasks MCP, monthly |

*(The fourth, `reilly-outbound.md`, was self-declared DEPRECATED since 2026-08-07 and moved to `_archive/`
on 2026-08-23 — it was the only unpaired SOP with no reason to be unpaired.)*

## Conventions

- One SOP per file, named `<topic>.md`. Keep them **executable** — a process nobody can follow without
  help isn't a process, it's a note.
- A loop SOP goes in `loops/`, gets a prompt in `runtime/prompts/`, and gets registered in
  `runtime/agent-registry.json`. The skill `.claude/skills/add-runtime-loop/` does all three; use it
  rather than doing it by hand, because half-wired is the known failure mode.
- **When an SOP dies, `git mv` it to `_archive/`** and add a row to that folder's `_README.md`. Do not
  leave a doc whose own first line says DEPRECATED sitting in a live folder.
