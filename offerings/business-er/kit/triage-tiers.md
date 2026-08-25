# Triage-tier definitions — Business ER (frontier #12)

> **STAGED — internal until launch (OtherVenture) + this offering's own trigger** (post-launch AND first 3–5 white-glove engagements complete). This file is the triage agent's tier rulebook and the source of Kolby's discrimination eval set. The phone number comes last.

## The test, before the tiers

The agent's first job is one question: **what stops, and when?** A T1 case names a stopping core function and a date. No named stopping function with a date = not T1, whatever the caller's tone. Panic is not a tier; a stopped function is.

## The tiers

### T1 — true operational emergency
A core function is stopped, or stops within days. **Response:** same-day human callback; 72h-free stabilization if accepted and within capacity (see `capacity.json` — the agent reads the config and may not override it).

Qualifying examples (from SPEC §1):
- The office manager quit with no notice and she was the only one who knew billing. *(Stops: billing. When: already stopped.)*
- The scheduling system died Friday and forty jobs are unassigned Monday. *(Stops: dispatch. When: Monday.)*
- The one estimator is in the hospital and bids are due this week. *(Stops: bidding. When: the due date.)*

### T2 — urgent but schedulable
Real pain, no cliff. **Response:** honest reframe on the call ("this is urgent, and it's not an emergency — here's the fast normal path"), audit CTA, CRM warm lead. Never the free window.

Examples:
- "We're drowning in intake, it's been bad for months." *(Nothing stops on a date; it's chronically painful.)*
- "Our bookkeeper retires at the end of next quarter." *(A cliff, but weeks-to-months out — schedulable continuity work, and the natural Understudy conversation.)*
- "We keep missing calls after hours and losing jobs." *(A leak, not a stoppage.)*

### T3 — sales call in disguise
Curiosity, price-shopping, vendors, tire-kickers. **Response:** courteous route to the standard funnel (site, demos, audit). Never enters the ER queue; never gets the free window; never gets ER treatment to win the deal (SPEC §8, no poaching).

Examples:
- "What would an AI employee cost for a business like mine?"
- "We're evaluating a few AI vendors and wanted to talk."
- "I saw the ER line and figured it was the fastest way to reach a human." *(Honest, and still T3.)*

## The discrimination that matters most: T3 dressed as T1

Misclassifying a shopper as an emergency is the failure mode that kills the offering — free consulting for tire-kickers, capacity burned, the line unanswerable for a real T1. The tells, each one eval-seeded (Kolby: seeded T3-as-T1 test calls in the weekly pass):

| Dressed-up claim | The unmasking question | Why it fails the test |
|---|---|---|
| "This is an emergency — we need AI *now*." | What stops, and when? | Urgency about *wanting a solution* is not a stopping function. |
| "Our receptionist situation is a crisis." | Is anyone answering the phone today? | If yes: T2 pain, not a stoppage. |
| "If we don't modernize we'll be out of business." | What stops *this week*? | A trajectory is not a date. |
| "Our competitor just got AI and we're behind." | — | Competitive anxiety names nothing that stops. Straight T3. |
| "We lost a big customer yesterday, everything's falling apart." | Did a core *function* stop, or did revenue take a hit? | Bad news is not a stopped operation. T2 at most. |

Borderline rule: a caller who *can't* name what stops gets walked through the question once, kindly. Still no named function + date → T2 or T3, stated honestly on the call. The agent errs toward the lower tier; a wrongly lowered T1 caller will say so ("no — payroll literally cannot run Friday"), and that correction re-triages cleanly. A wrongly raised T3 costs the whole line.

## Standing rules (all tiers)

- The immediate-guidance layer (checklist-grade stabilization steps the agent can safely give) is available to every caller, including at capacity, including T2/T3.
- Existing paying clients preempt: an ER case never degrades a paying engagement; if it would, the case waits or is declined, and the ER terms say so.
- Recording: explicit disclosure/consent at call start or no recording (FL two-party consent, per the gate-#1 recording rider).
- Every call becomes a CRM row from minute one, tier-tagged. T2s are warm leads; T3s route to the funnel; T1s open a case.
- No selling inside any T1 window, ever. The conversion conversation happens at the stability checkpoint (SPEC §3.4), never during.
