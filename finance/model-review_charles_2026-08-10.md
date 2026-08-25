# Model review — Charles, 2026-08-10 (evening)

**Scope:** `finance/yourco-financial-model.xlsx` as committed at `e395c5d`, after a day of heavy structural change (Jan-2027 start · three members at 50/35/15 · principal compensation · growing capacity ceiling · nine client targets · onboarding charged · four roles deleted · one hire type · capacity glide to zero · HQ editing).

**Verdict:** the model is mechanically sound *when calculated* — zero formula errors, and the Monthly P&L agrees with its Scenario Engines block to the cent across all 36 months. That matters more than usual today: rows were deleted three separate times and every reference remapped by hand, which is exactly the operation that produces silent wrongness. It survived.

But it was committed **uncalculated**, and there are four stale artifacts that will mislead a reader. One of them will waste somebody's afternoon.

---

## 1 · CRITICAL — the committed workbook had no computed values

`e395c5d` (21:00) made a real fix — Cash & Runway was counting two principals, not three — but wrote the file with **openpyxl and committed without recalculating**. openpyxl discards every cached value on save. The consequences:

- Anyone opening it in Excel sees numbers **only because Excel recalculates on open** — the file itself contained none.
- Every preview, Quick Look, Google Sheets import, or script reading it saw **blanks**.
- HQ's mirror was left pointing at a version of the workbook that no longer existed.

**The guards built this evening both caught it inside an hour**, which is the one encouraging thing here: `finance_model_sync.py` **refused to publish** — *"the workbook has no computed values"* — rather than writing zeros onto the dashboard, and `--check` went red. Neither is a substitute for the discipline. **Recalculate before committing; the three-surface rule in `agents/charles/_README.md` exists for exactly this.**

**Fixed in this commit:** recalculated, verified (6,839 formulas, 0 errors), re-synced HQ.

## 2 · A phantom salary input that does nothing

`Assumptions` carries **"Principal salary — annual, each" = $50,000**, with a derived **"→ all three, per month" = $12,500** beneath it, inside the COMPENSATION block. **Neither is referenced by any formula anywhere in the workbook.**

The salaries that actually drive the model are the three PEOPLE-block rows (the Founder / Partner B / Mike), which carry 312 references between them. Anyone opening the compensation block to change what the principals are paid would edit the phantom, see nothing move, and lose an afternoon to it. HQ's editor correctly targets the real rows — so the workbook and the dashboard currently disagree about which cell *is* "the salary".

**Recommend:** delete the two phantom rows, or relabel them "(display only — the live inputs are in PEOPLE above)". Deleting is better; a display-only duplicate of a number that can drift is a defect waiting to happen.

## 3 · Dead onboarding machinery, wearing a label that claims otherwise

The Monthly P&L still computes **"Onboarding hours consumed"** and **"→ delivery capacity consumed (client-equivalents)"**. Nothing references either. They were wired into delivery capacity when onboarding was first charged; the Founder's Advisor rule removed the draw so the principals' 50 could mean what he said it means.

The problem is not the dead cells, it is the **label**: a reader sees capacity being consumed by onboarding and concludes it constrains hiring. It does not. Two assumptions feeding them are dead for the same reason — *"Productive hours per head per month" = 160* and the derived *capacity consumed per new client = 3.75*.

**Recommend:** delete all four, or move the two P&L rows under a heading that says **memo — not wired into capacity**. The onboarding *dollar* cost is live and correct; only the hours half is orphaned.

## 4 · The engines still say "BASE CASE"

`Scenarios` says Conservative / **Target** / Aggressive. The Assumptions selector resolves to **Target**. The Scenario Engines block header still reads **"BASE CASE"**. Cosmetic, but this is the sheet somebody opens when they want to check the middle case by hand, and it is the one place the old name survives.

## 5 · The payroll burden is now vestigial

18% is referenced by exactly one thing: back-solving the Advisor's *implied annual base* (~$101,695), which is a display figure. **No person in the model carries burden** — principals draw salary with none applied, and Advisors are entered at $10,000/month already fully loaded. Add a burdened W-2 role later and the 18% will silently fail to apply.

**Recommend:** leave the cell, add a note that it is display-only today, and treat "does this role carry burden?" as a required question whenever a role is added.

---

## Economics — not defects, but the things I would be asked about

**Acquisition costs marginally more than the upfront collects.** At month 24: CAC $1,500 + onboarding $150 = **$1,650 per new client**, against net upfront of **~$1,558** (implementation fee less the 100% audit credit). Every client is **cash-negative at signing** and pays back out of retainer inside the first month or two. That is normal for a retainer model and it is fine at these volumes — but it is the first question a lender or a buyer asks, and the model should be able to answer it without arithmetic on the spot.

**The NOI line is flat at 48–50% across every case and every year**, because nothing in the model creates operating leverage in either direction: commission is a fixed 15% of revenue, connector commissions 5%, COGS is per-client, and Advisors are hired in lockstep with client count. A real services business's margin moves as it scales. Ours cannot, by construction. Read the flatness as an artifact, not a finding.

**COGS at $300/client/month is the single most consequential unvalidated input**, and Sample Product's own ledger models real run cost at **$15–40**. It may be wrong by ~10× in the *favourable* direction. The Actuals tab exists to settle it and currently reads *"not enough data"* — correctly.

**Peak cash need of $1,528 is real but flattered.** It charges nothing for principal time before the salary trigger, and excludes legal, CPA, insurance, payment processing and taxes — all named as absent in the Read Me. The other session's fix improved this materially by counting three principals rather than two.

**From month 24 the plan assumes zero principal involvement in delivery** — 118 clients rising to 190, carried entirely by 6 then 10 Advisors. That is the most valuable structural choice in the model (owner dependence is the dominant discount on a business this size) and simultaneously its least proven operational claim. It rests on an Advisor genuinely carrying 20 clients, which no one has ever done here.

---

## What I would fix, in order — ALL CLEARED 2026-08-10 (the Founder)

1. ~~Recalculate and re-sync~~ — **done.**
2. ~~Delete the phantom salary rows~~ — **deleted** (Assumptions ×2).
3. ~~Relabel or delete the dead onboarding-hours rows~~ — **deleted** (P&L ×2, Scenario Engines ×3, Assumptions ×2). The onboarding *dollar* cost is untouched and still flows into opex.
4. ~~Rename "BASE CASE"~~ — **now TARGET CASE**, subtitle fixed with it.
5. ~~Note the payroll burden as display-only~~ — **annotated** at the assumption.

**How it was verified.** 77 headline outputs were snapshotted before the cleanup and compared after: **identical**, which is the only acceptable result when the premise is that every deleted cell was dead. A guard refused to delete any row still referenced by a surviving formula — and it fired once, on the phantom's own derived row, before being narrowed to ignore references from rows that were themselves being removed. 182 dead formulas went out (6,839 → 6,657), zero errors remain.

**One orphan was created and kept deliberately.** Removing the capacity draw left *"Principal/operator hours per new client" = 30* referenced by nothing. It is retained as the **benchmark the Actuals tab's measured hours are compared against**, and — unlike the phantom salary that caused finding §2 — it is now labelled *"(benchmark — not wired)"* with a note saying changing it moves no output. An unwired input is only a defect when it pretends otherwise.

**Standing note for whoever edits next:** Excel reporting zero errors is not evidence the numbers are right. Snapshot the headline figures before a structural change and diff them after — that comparison, not the error count, is what caught today's real bugs.
