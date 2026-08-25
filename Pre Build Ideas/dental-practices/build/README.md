# Chair OS — build 3 of 10

Pre-built vertical AI OS for general dental practices and small DSOs.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py                      # 1,900 patients, 24 months, a real ledger
python3 test_chair_os.py             # 44 assertions, every one a refusal
```

Launch name **`prebuild-chair-os`** (port 8823, 127.0.0.1 only).

## What it is

"Northcutt Family Dental" — two doctors, four hygiene chairs, ~1,900 patients, **$865k of
diagnosed-but-unscheduled treatment sitting in the ledger**, four invented payers with different
rule sets. All synthetic.

Four engines: **unscheduled-treatment ranking**, **same-day fill**, **benefits pack**, **recall
watchtower** — plus the chair board.

## The two prohibitions, enforced as rules

**No insurance determination.** `verify()` returns each field as either something the payer
returned or `unconfirmed` with the reason, and `can_state_coverage()` is the single gate on telling
a patient anything. Keystone Administrators never answers, so its patients read unconfirmed on
every field. A patient with no enrollment date on file makes the waiting period *unknowable* — it
is never assumed satisfied. The eval measures exactly one thing: benefits reported as confirmable
when the payer never confirmed them. It must be zero, and it is.

The counter-discipline matters as much: a responding payer returns its whole rule set, so the
*absence* of a frequency limit or a downgrade rule is an **answer**, not an unknown. Over-refusing
would make every sheet an exception and the exception list stop meaning anything. (This was a real
bug on the first run — 30 of 30 sheets came back unconfirmable.)

**No clinical opinion.** `clinical_opinion` is declared in the matrix at **R0 / never promotes** so
a buyer can read the prohibition rather than trust it. There is no code path that produces a
recommendation; the build only moves treatment a dentist already diagnosed, and the reactivation
copy quotes the diagnosing doctor and the tooth, nothing more.

## The constraint most schedule-filling tools ignore

A hygiene opening cannot be filled with a crown. `fits()` checks the **chair type and the minutes
before value**, and `accept_fill()` refuses a mismatch even when asked directly. The refused
candidates are shown with their reason ("needs a dds chair, this opening is rdh") rather than
silently ranked lower. Candidates are then ordered by *who will actually come* — flexible list,
short-notice history, travel time — before fee, because a $2,450 implant that cannot get here in
forty minutes fills nothing.

## Other refusals

- Every ranking component is printed next to the patient, including the *absences*: "responsiveness
  not recorded", "benefit year end not on file".
- A patient with no hygiene history is never called overdue.
- Holes are valued at the best-fitting unscheduled treatment **for that chair**, not at an average.
- "Recovered" counts only production whose event log shows an agent touch before the booking.
- Verification savings are hours, reported apart from production and never summed into it.

## 10-minute demo

1. **Tomorrow** — scheduled production, two holes and what they are worth, three verification
   exceptions, and $865k on the ledger.
2. **Unscheduled treatment** — the ranked queue with every scoring component visible; draft the top
   25 and read the copy (the doctor's words, the tooth, and the benefit-expiry note only where the
   benefit year is genuinely closing).
3. **Same-day fill** — build the ASAP list for the hygiene hole: only hygiene-chair treatment, in
   waves, with the refused implants shown and named. Accept one and see the time-to-fill.
4. **Benefits pack** — tomorrow's 30 sheets, the three that could not confirm, and the
   *can we state coverage?* column that is the whole point.
5. **Recall** — benefit-expiry hooks first, then "not flagged" and why.
6. **What it's worth** — three revenue lines and one time line, never summed.
7. **Trust & audit** — the queue, the eval, `clinical_opinion` sitting at R0, the append-only log.

## What this does not do yet

- **No integrations.** Open Dental / Dentrix / Eaglesoft and the eligibility clearinghouse (270/271)
  are adapter seams. Nothing has spoken to a real payer.
- **Payer rules are modelled, not real.** Four invented payers with plausible rule shapes; a real
  deployment needs the practice's actual plan table.
- **No claims, no billing, no treatment planning.** This build moves what is already diagnosed.
- **No HIPAA infrastructure.** Live deployment needs counsel review and a signed BAA; the prototype
  avoids the question with synthetic records.
- **Nothing is sent.** Reactivation copy is drafted behind the gate.
