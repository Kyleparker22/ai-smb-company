# /decisions/

> ⚠️ **NOT YOURS YET.** Every file here is a decision **the source company made** — kept because the *format* is the
point: what was chosen, why, and the trip-wire that would make it wrong. They are not your
decisions and several will not apply. Read two or three, then start writing your own with
`.claude/skills/log-decision/`. Delete the rest whenever you like.


The decision log. It answers the future-the Founder question **"wait, why did we decide X?"** — and it is
load-bearing, not archival: `dashboard/tripwires.py` evaluates these files against live facts,
`dashboard/lockin.py` derives lock state from them, `rejections/` is their mirror image, and
`runtime/consistency-check.py` verifies that every citation of a decision anywhere in the repo
resolves to a real file.

One decision per file, `YYYY-MM-DD_<short-slug>.md`, starting `2026-06-07`. For the live count and
coverage, run `python3 dashboard/tripwires.py` — it prints both and is never out of date; numbers
quoted below are a **snapshot taken 2026-08-24** and are here to show the shape, not to be current.

---

## What a decision file contains

Described as it **actually is**, not as an ideal — measured across all 113 files on 2026-08-24. The
previous version of this page listed five required sections; the log has never matched it, and a
convention doc that describes a third of the files makes a reader think files are broken when the
convention simply moved.

| Section | In | Notes |
|---|---|---|
| `## Why` | 79 / 113 | The reasoning that won. The one section worth insisting on — the rest can be reconstructed, this cannot. |
| `## Decision` | 65 / 113 | What was decided, in one sentence. |
| `## Addendum` | 44 / 113 | **How a decision evolves.** A settled call that later gained a caveat, a number, or a partial reversal gets an addendum rather than a new file. Second most common heading here, and it was undocumented until 2026-08-24. |
| `## Reversibility` | 42 / 113 | The predecessor of the trip-wire — prose about what would prompt a revisit. Still fine; not machine-readable. |
| `## Context` | 34 / 113 | What was happening that prompted it. |
| `## Options considered` | 29 / 113 | Alternatives, briefly. |
| **`## Trip-wire`** | **24 / 113** | **The current rule.** See below. |

## The Trip-wire — the current rule

`07_RULES.md`: *made a settled call → a dated file in `decisions/`, **with a `## Trip-wire`** naming
what would reopen it.* Format and the list of available facts: **`_TRIPWIRES.md`**.

A trip-wire is a machine-checkable expiry condition. `dashboard/tripwires.py` evaluates every one
against live company facts on each poll and reports `contradicted` / `due` / `watching` /
`unreviewed` / `uncovered`.

**Coverage was 24/113 at the last count, and low coverage is deliberate.** The seeded trip-wires are *transcriptions* of revisit
conditions the files already stated in their own words. Decisions whose condition is qualitative
carry the prose with no machine check, and **decisions that never stated one are left `uncovered`
on purpose** — backfilling would mean inventing a reopen condition after the fact, which is exactly
the fabrication this OS exists to refuse. The coverage number is a to-do list for the Founder, not a gap to
paper over.

**A fired trip-wire now lands on The Board** as `needs-you` (added 2026-08-24). Before that, the
only reader was the weekly `evidence-sweep` loop — and while it was paused a trip-wire fired on the
three-member partner split and no surface a human opens said so.

## When a decision dies

Mark it **at the top of the file**, before anything else, naming what replaced it:

```
**Status:** ⛔ SUPERSEDED 2026-06-30 by `decisions/2026-06-30_multi-client-scaling-locked.md`
```

Six files carried one at the last count. **Never delete a superseded decision** — the reasoning is the asset, and
the fact that we changed our mind is itself a finding. Partial supersession is normal; say which
part (`⚠️ PARTIALLY SUPERSEDED …: the OpenMontage adoption is reversed; the realism call stands`).

## What's worth logging

- Scope, pricing, ICP, vertical focus
- Anything touching the moat (eval, watchdogs, approval flow, autonomy rungs)
- Anything pulling toward a parked direction (especially self-serve SaaS)
- Structure, ownership, partners, capital
- Hiring; toolstack changes; `yourco-template` upgrades

## The sibling folder

**`rejections/`** is the anti-library — what we decided *not* to do, each entry carrying the
condition that would reopen it, in this same trip-wire grammar and evaluated by the same engine.
Every idea-generating loop must clear it before proposing. **A decision records a road taken; a
rejection records one refused.** If you are about to write "we considered X and said no," it belongs
there, not here.
