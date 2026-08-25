# The Capacity Board — Build Spec

**Working name:** The Capacity Board (frontier #27)
**Author:** the Founder
**Stack:** no new runtime — `runtime/capacity.py` (built 2026-08-08) reads `loops/_build-journal/sessions.jsonl` for measured build hours and the CRM for engagements already in build; emits either a Monday slot date or a refusal
**Status:** **BUILT — and currently refusing.** Roadmap row #27. It will not quote a date until three *measured* build sessions exist; all three journal entries today are backfills.
**Pillar / form factor:** Sales (pillar 2); form factor 3 (a line in a conversation, or a short shared artifact).

---

## 1. Concept

"We're pretty booked" is the most common lie in professional services, and buyers have learned to price it at zero. Manufactured scarcity is so universal that real scarcity has no way to signal itself.

yourco can compute it. `log-build-session` records how long real builds actually take. Median build hours ÷ available build hours per week × engagements already in build = **a date**. Not "we're busy" — *"the next onboarding slot that isn't a lie is October 6."*

Which converts a stall for a structural reason rather than a psychological one: a deal that sits now costs the buyer a **dated slot**, and the date is one they can check the arithmetic on. The assumptions are printed underneath — build capacity per week, no parallel-build discount — because a scarcity claim whose inputs are hidden is the original lie wearing a spreadsheet.

**The refusal is the product.** Run today, the board says: *"NEXT SLOT: not stated. 0 measured build sessions on record; 3 is the minimum this instrument will quote from… A capacity board exists to make scarcity checkable. Quoting a date from a sample this thin would make it exactly the claim it was built to replace."* It then names precisely what would fix it: three builds timed with `--start`/`--stop` rather than reconstructed afterwards.

## 2. Why it's never been done

Agencies do capacity planning constantly — internally, for staffing. It never becomes a customer-facing number for two reasons, one honest and one not.

The honest one: most firms genuinely cannot compute it. Utilisation data lives in timesheets nobody trusts, project scope is elastic, and "how long does a build like this take" is answered from memory by whoever is asked. The dishonest one: a *computed* slot date is falsifiable, and vagueness is commercially useful — it can be tightened when a deal needs urgency and loosened when it needs patience.

yourco can do it because the build journal was created for a different purpose (estimating future builds from evidence, `.claude/skills/log-build-session/`) and already enforces the discipline that makes the number honest: **backfills are excluded from hours medians, and below three timed sessions `--estimate` refuses.** The capacity board inherits that threshold rather than inventing a friendlier one. The willingness to publish a refusal instead of a date is the part no competitor will copy.

## 3. Build shape

| Piece | What it is | Status |
|---|---|---|
| Evidence loader | Reads the append-only journal, applies `session.correction` records, classifies each session `measured / stated / backfill / unknown` | **built** |
| Median + range | Median build hours from **measured sessions only**; the range is reported alongside and named as the honest signal at small n | **built** |
| Commitment side | Engagements at `build`/`signed` in the live CRM consume capacity | **built** |
| Slot arithmetic | `backlog_weeks = committed × (median ÷ hours_per_week)`, snapped forward to a Monday — a mid-week onboarding date isn't a real one | **built + tested** |
| Refusal path | Below 3 measured sessions: no date, the reason, the count, and the exact command that would fix it | **built — currently the live output** |
| Assumptions block | Weekly build hours (a stated assumption, flagged as unmeasured until the Founder confirms) and the no-parallel-build rule, printed with every run | **built** |

**Effort band:** XS to build. The real cost is behavioural: **timing three builds properly**, which nothing but discipline produces.

## 4. Moat fit

- **Honesty as a closing instrument.** The board is only persuasive because it is checkable, and it is only checkable because yourco instruments its own work. That is the moat pointed at the buyer.
- **It prices the Founder's time correctly.** A solo founder's binding constraint is hours; a capacity board makes that constraint visible to the buyer instead of absorbed silently as free urgency.
- **It protects delivery.** The same number that creates sales urgency also stops over-committing — the failure mode that would kill engagements #2 and #3 (`processes/delivery-surge-playbook.md`).
- **It compounds with the model-upgrade dividend:** as builds get faster, the slot date moves closer and the capacity number rises, visibly, from measured evidence.
- **Interlocks:** the build journal (existing); the Simulated Company (#22) is what fills the wait; Trust Ledger (#1) is the same posture at company scale.

## 5. Gates / compliance

- **No counsel gate.** A number quoted in a 1:1 conversation.
- **Never quoted from backfills or stated-from-memory hours** — enforced in code, not by intention. A backfill records what someone remembered, not what was measured.
- **The weekly-build-hours input is an assumption until the Founder sets it**, and prints as such on every run. It is currently defaulted at 20 h/week and explicitly labelled unmeasured.
- **No public publication of the slot date** pre-launch (OtherVenture). It travels in conversation and in proposals, not on the site.
- **If the board is wrong, it is corrected in public with the client** — a slot promised and missed does more damage than no slot, so a missed date gets a stated reason and a new computed one, never a quiet reschedule.

## 6. Pricing frame

**Not priced.** It is an input to the sale and to delivery planning. Its commercial effect is on *close rate and sequencing*, never a line item.

## 7. Activation trigger (build)

**Built; activation is gated on evidence, not on code.** The trigger to *use* it is three build sessions timed in real time. Given one engagement folder per active relationship and real build work happening weekly, that is a few weeks of discipline, not a project. Until then the board's own output is the instruction, and quoting any slot date from memory in the meantime is the specific thing this instrument exists to stop.

## 8. What we will NOT do

- **No slot date below three measured sessions.** Not "roughly," not "probably October," not a range hedged into vagueness. The instrument refuses, and the refusal is what gets said out loud.
- **No backfilled or remembered hours in a median.** Ever.
- **No hidden assumptions.** Weekly build hours and the no-parallel-build rule print with every run; a scarcity claim with concealed inputs is the lie this replaces.
- **No manufactured tightening.** The date is not moved closer because a deal needs urgency. It is recomputed when the inputs change, and only then.
- **No slot sold twice.** If a slot is offered to two prospects, both are told it is contested and on what basis it resolves.
- **No public scarcity marketing** — no countdowns, no "2 slots left" on any surface, pre- or post-launch. It is a fact stated in a conversation, not a conversion tactic.
