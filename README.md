# AI SMB Company — build a small business on an AI agent workforce

**You are starting from zero.** This is not a running business — it is the **scaffolding and the
instructions** for building one: the folder structure, an always-on agent runtime, ~21 reusable
skills, a CRM with an insight layer, a command dashboard, 76 industry prototypes, and a thirteen-part
guide that takes you from forming an entity to the guardrails that keep the whole thing honest.

Extracted from a real company's operating repo, with every identifying detail replaced.

## Start here

1. **[`SETUP/00_START-HERE.md`](SETUP/00_START-HERE.md)** — the build, in dependency order. Each step
   ends with a **Done when** you can point at.
2. **`RENAME-THIS-FIRST.md`** — replace the placeholders before you build on top.
3. **`CLAUDE.md`** — the boot context every agent session loads. **It is a fill-in-the-blanks file.**
   Write it early; an agent reasoning from an empty or borrowed boot context will be confidently wrong.
4. **`00_README.md`** — the map, and the **five reality levels** that separate real records from
   examples. Read this before you trust anything in the repo.

**Shortest path to something real:** steps 01 → 03 → 04, then the first half of 05. That gets you one
loop on a timer writing one artifact — the smallest complete version of the whole idea.

## What comes in the box

| | |
|---|---|
| `SETUP/` | the thirteen-part build guide |
| `runtime/` | loop machinery — systemd units, approval gate, the run wrapper |
| `.claude/skills/` | procedures an agent invokes instead of being re-told |
| `crm/` · `dashboard/` · `app/` | a CRM with seven insight reads, a dashboard, a role-gated gateway |
| `agents/` | a 27-agent roster, all marked **not built** — a menu, not a fleet |
| `processes/` | SOPs — delivery, the diagnostic call, outbound, partnerships |
| `finance/legal-docs/` | **blank forms**: business info, insurance, counsel review, valuation |
| `finance/*.xlsx` | a starter model — assumptions, P&L, runway, unit economics |
| `Pre Build Ideas/` · `offerings/` | 76 prototypes on synthetic data, 33 build specs |

## What is NOT yours

The repo ships with worked examples so you can see the shape of each thing before you build it. **All
of it belongs to the company this came from and is labelled where it appears:**

- **`_EXAMPLE_` files** — one real output per loop, so you can see what a run produces
- **`clients/`** — three engagements with names, domains and locations removed
- **`decisions/` and `learnings/`** — their reasoning, kept because the *format* is the lesson
- **`_ORIGINAL-CLAUDE.md`** — their boot context, kept as an example of how specific yours should get

Replace or delete each as you go. Nothing breaks if you delete all of it.

## What was removed

No EIN, bank details, signed agreements, registered address, API keys, or real contacts. See
**`WHAT-WAS-REMOVED.md`** — including the four ways an identity survived a naive scrub, which is
worth reading if you ever publish something extracted from your own repo.

## The honest caveat

The source company was **pre-revenue** — no signed clients, no referral partners, no salespeople. The
machinery is real and runs. The *results* did not exist. Where a page describes an outcome it is
describing an intention, and it says so.

Keep that habit in your own version. A system that tells you what it cannot prove is worth more than
one that quietly implies it can.

**License:** MIT. **No warranty.** Nothing here is legal, tax, or financial advice.
