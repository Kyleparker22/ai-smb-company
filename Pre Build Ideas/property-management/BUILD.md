# Property OS — residential property management (moved from `offerings/`, 2026-08-24)

> **This one did not start here.** It was specced and then fully built inside `offerings/`, which is
> the folder for things we have *described*. At 81 files and ~8,460 lines of Python it had stopped
> being a spec, and `offerings/_README.md` had already named it as an exception that should move.
> This is that move. **Nothing about the build changed** — 485 assertions passed before it and 485
> after.

## The bleeding neck
A manager holding **20–300+ units** runs three loops at once and has staff for none of them:
**maintenance** (intake → triage → dispatch → proof → invoice), **leasing/turnover** (notice →
make-ready → measured vacancy), and **money** (rent → delinquency ladder → trust ledger →
statements → drafted disbursements). Ten agents run all three; everything a human still decides
collects in one queue that says *why* a human is required.

## The trust ramp this build is missing (2026-08-24)

**Alven.AI** ships this exact product with revenue, and does one thing better than we do:

> *"When leads call, **your phone rings first** — Alven only picks up if you miss the call."*

The owner never surrenders the call. The AI catches only what would otherwise be lost, so adoption
costs the buyer nothing and the agent earns the next rung on evidence they can see. That is yourco's
autonomy matrix (R1 floor → earned) expressed as a **feature a buyer can feel**, rather than a
governance concept in a doc. It is a paragraph of design, not a build.

Triage + the competitive read: `loops/_triage/2026-08-24_batch-ten.md`.

## Guardrails (load-bearing)
- **It accounts for money and prepares movement. It never moves money.** Executing a transfer is
  permanently **R0** — a human does it at the bank and records that they did, with a bank reference.
- **The trust ledger is bookkeeping software, not a compliance program.** State trust-account rules
  bind the operator; counsel/CPA review gates any use with real funds.
- Synthetic portfolio, zero clients, zero real data.

## Why it is the reference build
**Thirteen other pre-builds cite it** — their `BUILD.md` says to mirror this one. It is the fullest
worked example of the pattern in the repo: three loops, ten agents, a human queue that explains
itself, and a money rail that refuses. Read it before starting a new build.

## Demo path
`./show.sh` or launch **`prebuild-property-management`** from `.claude/launch.json` (`:8813`).
The honest limits, the module map and the money rail are in **`build/README.md`** — the canonical
description, kept there rather than copied here.

## Tests
```
cd "Pre Build Ideas/property-management/build"
python3 test_propertyos.py    # 272 assertions
python3 test_journeys.py      # 213 assertions
```
