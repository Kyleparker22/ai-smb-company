# 03 — The repo: the company's brain

> **Build step 03.** Nothing here is done yet. Where this page shows a filled-in value, that is
> the source company's — replace it with yours.

## What it is

This repository **is** the company. Not documentation about the company — the operating substrate the
agents read, write, and reason over. `finance/` is the books, `clients/` is the engagements, `loops/`
is what the machine did while nobody watched, `decisions/` is why anything is the way it is.

Get this right early. Every step after it writes here, and retrofitting structure onto a year of
accumulated files is far more expensive than choosing it on day one.

## The four files that carry the load

| File | Job | Read it |
|---|---|---|
| `CLAUDE.md` | The always-loaded boot context. Every session starts with it in context. Dense, current, edited first when anything changes. | first |
| `00_README.md` | The **human** front door. Five reality levels, every folder, read-in-this-order. `CLAUDE.md` is the machine's boot file; this is the person's. | first |
| `07_RULES.md` | The rules index — the six places rules actually live, and the "when you do X, update Y" table. Points at sources, never copies them. | when you need to change a rule |
| `06_business-plan.md` | The plan, the projections, **the 17 owner's rules and the 12 core principles**. | when you need to know what the company believes |

## The reality levels — the single most important idea here

`00_README.md` opens by warning that several folders look alike and mean completely different things.
Get this wrong and **you will treat a prototype as a product**:

| Level | Folders | Means |
|---|---|---|
| 🟢 **REAL** | `clients/` `crm/` `finance/` | actual engagements, actual numbers |
| **DOCTRINE** | the 00–07 spine, `processes/`, `.claude/skills/` | how the company says it works |
| **DECIDED** | `decisions/` `rejections/` `learnings/` | settled calls, refusals, observed patterns |
| **BUILT** | `Pre Build Ideas/` `app/` `dashboard/` `runtime/` | built, unsold |
| 🟡 **DESCRIBED** | `offerings/` | argued, never built |
| **RECORD** | `loops/` `daily-logs/` | dated artifacts — true when written |
| ⚫ **DEAD** | `_archive/` | history only; never cite for current state |

This is not decoration. `runtime/kb.py` ranks every search result by these levels precisely so a
confident hit in `Pre Build Ideas/` cannot read like a confident hit in `clients/`.

## The three memory surfaces, and choosing between them

Every reusable thing goes to exactly one of these. The test is in `.claude/skills/create-skill/`:

- A **choice** was made → `decisions/YYYY-MM-DD_slug.md`. **Write its trip-wire** — the condition that
  would make it wrong (`decisions/_TRIPWIRES.md`).
- A **pattern** was observed → `learnings/<domain>/`, with `Triggers:` so it loads when relevant.
- A **procedure** worth repeating → a skill in `.claude/skills/`.
- Something **ruled out** → `rejections/`, the anti-library, each entry carrying its reopen condition.

And, added 2026-08-24: something you have **not decided where to put** → `inbox/`. It is the only
folder that does not demand the routing answer at capture time.

## The rule you will break, and the machine that catches it

**Change-one-sweep-all.** Canonical facts are duplicated across surfaces — site pages, packets, specs,
CRM meta, `CLAUDE.md`, decisions. When you change one, **grep the repo and update every surface in the
same commit.** A fact changed in one place and stale elsewhere is the #1 cross-session failure mode.

Two machines back this up, and both fired repeatedly on the day this guide was written:
- `runtime/consistency-check.py` — 83 invariants, Monday 07:40 ET. **When a human catches drift by
  eye, add it here so it is never caught by eye twice.**
- `runtime/doc_claims.py` — documents that declare their own checks. A number carries its own
  verification inline, so the doc and the check live in the same edit.

## Git model — two machines, one main

This Mac and the VPS runtime are separate clones, both pushing to `main`. Always pull `--rebase`
before push. `loops/` artifacts are runtime-owned — prefer the runtime's copy on conflict. **Never**
`git reset --hard`.

**Within a machine, multiple sessions share one clone.** To commit your own work:

```bash
runtime/commit-scoped.sh "message" path/one path/two
```

**Never bare `git add -A`** — it sweeps other concurrent sessions' in-progress files into your commit
and buries them. This is not hypothetical; on the day this was written, another session had uncommitted
contract edits sitting in the tree the whole time.

## Done when

**this repo is renamed, `CLAUDE.md` describes YOUR business, and you have made one commit.**

If you cannot point at that, the step is not finished — do not move on.
