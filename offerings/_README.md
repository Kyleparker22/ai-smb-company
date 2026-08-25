# offerings/ — things we have **described** but not built

> ⚠️ **NOT YOURS YET.** Build specs the source company **wrote but never built.** Reality level: DESCRIBED. Treat as
idea inventory, not product.


> **Reality level: DESCRIBED.** Every folder here is a spec. Nothing here is sold, nothing here
> has a client, and — with the three exceptions named below — nothing here runs.
> A spec is cheap to write and cheap to be wrong about. Treat these as arguments, not assets.

## The line between this folder and `Pre Build Ideas/`

Written down 2026-08-22, because it never had been and the two folders had started to blur:

| | `offerings/` | `Pre Build Ideas/` |
|---|---|---|
| What it is | a thing we **described** | a thing we **built** |
| Contents | `SPEC.md` — the argument, the mechanism, the open questions | `BUILD.md` + a running `build/` on synthetic data |
| Test | can you read it? | can you *launch* it from `.claude/launch.json`? |
| Neither is | sold. Both are n=0. | |

A new idea starts **here** and *moves* to `Pre Build Ideas/` when someone builds it.

⚠️ **Two folders have crossed and not moved** — the exception to watch, not the pattern to copy:
`trust-ledger/` (`generate.py` + prototype) and `autonomy-standard/` (`STANDARD-v0.md` + prototype).
Both are small, both are launchable, and both should move when someone next touches them.

**`property-os/` was the third, and it moved on 2026-08-24** → `Pre Build Ideas/property-management/`.
It had reached 81 files and ~8,460 lines of Python — an operated OS for one industry, which is
precisely the `Pre Build Ideas/` unit — while sitting in the folder whose README says nothing here
runs. This page had already set the trigger ("if a fourth one crosses, move it"); the honest reading
was that three was already too many, so the largest one went first. 485 assertions passed before the
move and 485 after. `runtime/consistency-check.py` now flags any `offerings/` entry that registers a
runnable server, so the next crossing announces itself instead of waiting to be noticed.

## What's in here

**33<!--#count: dirs offerings/*--> offerings.** 30<!--#count: files offerings/*/SPEC.md--> carry a `SPEC.md`. Three don't: the two above, which outgrew the format into running prototypes, plus `local-mesh/`, which carries an `ARCHITECTURE.md` instead — it never crossed into a prototype, so it is not an exception to the move rule.

`_frontier-roadmap.md` is the sequencing layer — **the Frontier Board**, 29 never-been-done offerings
adopted 2026-08-06 with a status board and a build trigger for each. **Read it before starting anything
in here**, because it already says what is being built now and what is deliberately waiting on a trigger
(usually "first signed client"). Building out of that order is how a pre-revenue company runs out of runway.

## Before you add one

1. **Check `rejections/` first** — the anti-library. If the idea was already declined, the entry names
   what would have to change to reopen it. Say either "not previously rejected" or name the file and
   what changed.
2. **Write a `SPEC.md`**, not a folder of fragments. If you can't write the spec, the idea isn't ready.
3. **Give it a build trigger** — the condition under which it stops being a spec. An offering with no
   trigger is a daydream with a folder.

## The honest counter-argument, kept in view

Thirty-three specs and seventy-one prototypes at **zero clients** is a lot of inventory for a company
whose bottleneck is a single unsigned proposal. Sample Client converting moves yourco further than any
folder in here. Specs are cheap — that is the defence — but attention is not.
