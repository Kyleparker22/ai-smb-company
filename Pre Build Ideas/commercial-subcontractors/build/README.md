# Change OS — build 11

Pre-built vertical AI OS for commercial trade subcontractors.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py              # 25 projects, ~150 field notes, 140 pay apps
python3 test_change_os.py    # 39 assertions
```

Launch name **`prebuild-change-os`** (port 8831, 127.0.0.1 only).

## What it is

"Meridian Mechanical" — $14M mechanical sub across TX/FL. Five modules: **change-event capture**,
**CO ledger**, **retainage watchtower**, **notice & lien calendar**, **invitation triage**.

## The refusal it is organised around

**A change order with no written authorization on file cannot be submitted.** The system drafts it,
values it, and then refuses to send it — with the reason: a verbal CO submitted in writing becomes
a dispute, not a payment. The refusal is logged; it never becomes a row with an Approve button.

Also load-bearing:
- **Every deadline is a DATE ALERT, not legal advice**, computed under per-state rules that name
  themselves a default and say "replace with counsel-reviewed rules before go-live." A state with
  no rule set, or a project with no furnishing date, is *uncomputable and says so*.
- `file_lien` / `file_notice` / `assert_entitlement` are **R0** — counsel files, humans take legal
  positions.
- GC pay speed is a median from *this sub's own ledger*, refusing below 4 paid apps — reputation is
  not a number.
- No schedule of values → % complete is unknowable, never estimated.

## The eval

Change-event capture on 13 labelled field notes; the costly class is the **missed change event**
("MONEY NEVER BILLED"), reported alone. Bias is over-flagging on purpose: a false flag costs a PM
thirty seconds.

## 10-minute demo

1. **Board** — unbilled change value, retainage past terms, next deadlines, all counted.
2. **Change orders** — the demo CO (super's direction, nothing signed): click Submit, watch it refuse.
3. **Retainage** — held dollars aged from substantial completion.
4. **Notice calendar** — computed dates, the GA project honestly uncomputable, the rule set named
   replaceable.
5. **Invitations** — go/no-go with pay-speed receipts.
6. **Trust & audit** — eval, matrix (three never-promote legal actions), append-only log.

## What this does not do yet

- **No integrations.** Foundation/Procore/Textura, email intake for field notes are adapter seams.
- **Classification is deterministic pattern-matching** — right for the audit trail, too brittle for
  the long tail of field prose. A real deployment puts a model behind `classify_note()` and keeps
  the submit refusal exactly as it is.
- **Notice rules are simplified shapes, not law.** Counsel replaces the rule set per state before
  any client sees a date.
- **Nothing is sent.**
