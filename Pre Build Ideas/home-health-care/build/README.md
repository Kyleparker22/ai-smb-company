# Shift OS — build 10 of 10

Pre-built vertical AI OS for private-duty home care and small home health agencies.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py                      # 210 caregivers, 140 clients, 12,900 shifts
python3 test_shift_os.py             # 96 assertions, every one a refusal
```

Launch name **`prebuild-shift-os`** (port 8830, 127.0.0.1 only).

## What it is

"Willowmere Home Care" — $6.5M private-duty, 210 caregivers, 140 clients, 484 approved pairings.
Six modules: **fill engine**, **message triage**, **retention watchtower**, **EVV exceptions**,
**family loop**, **referral desk**.

## The strictest guardrails in this set

**The crisis stop.** Fall, chest pain, breathing difficulty, unresponsiveness, stroke signs,
bleeding, self-harm, suspected abuse — each typed, each routing to a human **immediately**, each
showing the emergency instruction (*"If this is an emergency, call 911 now…"*). The system does not
assess, does not reassure, does not advise; all three would be practising nursing, and the reply
records that it refused. Eval: 13 cases, recall **1.0**, **zero missed** — and the eval names the
stake in its own text: *A MISSED CRISIS IS THE WORST FAILURE THIS SYSTEM CAN PRODUCE.*

**Suspected abuse** additionally raises a mandatory-reporting flag carrying the sentence
*"reporting decisions are never made by software"*. `mandatory_report` is R0.

**No clinical advice.** Dosing, medications, blood pressure readings, wounds, "is she getting
worse", care-plan changes — all routed to a nurse unanswered. An empty or unreadable message routes
too. `clinical_answer` is R0 / never promotes.

**A caregiver is never auto-assigned to an unapproved pairing.** `accept_fill()` refuses even when
the caregiver says yes — *"a stranger arriving unannounced is how a family starts shopping"* — and
`assign_new_pairing` is R1, never promoting.

**The system never messages a caregiver about retention.** `message_caregiver_retention` is R0: an
automated *"we noticed you seem unhappy"* is worse than silence.

## The fill engine

Ranked, explainable, overtime-aware. Approved pairings first, then score; every row carries its
reasons, and **every option that would trigger overtime shows what it costs on the row** — the
scheduler should not learn on Friday that the 6am fix cost time-and-a-half. Blocked caregivers are
shown with the blocker named: missing a care-plan skill, over the 40-minute travel line, or
previously declined by the family.

## Two numbers that were embarrassing until they were fixed

- **88% of the roster read "at risk."** A list that flags everyone is a list nobody works. One
  signal is now a note; **two is a pattern** — 106 at risk, and the 78 with a single signal are
  counted separately and said out loud.
- **58% of visits showed an EVV "exception."** Over-authorization was being evaluated per visit, so
  once a client passed their cap every completed visit was flagged, burying the real documentation
  gaps. It is now a **client-level** fact (39 clients past or near their cap) and visits are flagged
  only for what is actually missing on the visit.

**EVV rules are configurable per state.** Nothing hardcodes one state's requirements; the default
rule set names itself a default and says *"replace with the state's own rule set before go-live."*
A test proves the rules drive the exceptions — turn on `require_gps` and the exception appears.

## 10-minute demo

1. **Ops board** — 14 unfilled inside 72 hours ranked by client risk, overtime exposure, retention,
   EVV.
2. **Fill a shift** — simulate the 6:12am callout on the transfer-assistance client: three in wave
   one with reasons, the overtime cost on the row, and the new-pairing candidate flagged. Say yes on
   the unapproved one and watch it **refuse**.
3. **Family inbox** — handle *"she fell in the bathroom and I can't get her up"*: routed, 911
   language, nothing assessed. Then the bruises message: mandatory-report note. Then *"should she
   take her pill twice today?"*: routed unanswered.
4. **Retention** — 106 with two or more signals, each signal spelled out.
5. **EVV** — exceptions with their billing consequences, and the rule set named as replaceable.
6. **Trust & audit** — both evals, `clinical_answer` / `mandatory_report` /
   `message_caregiver_retention` at R0, the append-only log.

## What this does not do yet

- **No integrations.** AxisCare/WellSky/ClearCare/AlayaCare, SMS, payroll and the state EVV
  aggregator are adapter seams.
- **Classification is deterministic pattern-matching** — correct for the crisis and clinical stops
  (auditable, testable, biased on purpose) and too brittle for the long tail of how families
  actually write. A real deployment puts a model behind the routine path and leaves
  `read_message()`'s crisis half exactly as it is.
- **No scheduling optimiser, no route planning, no payroll.**
- **No HIPAA infrastructure.** Live deployment needs counsel review and a signed BAA; the prototype
  uses synthetic records only.
- **Nothing is sent.**
