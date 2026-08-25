# 2026-06-16 — yourco Care: a DTC offering/vertical (AI care-coordinator for aging parents)

## Decision (the Founder)
yourco adds a **direct-to-consumer offering**: an **operated AI care-coordinator** for the adult child managing an aging parent's life. It's an yourco offering/vertical — same substrate, same moat — pointed at a household instead of a business. Working name: **yourco Care** (Luka/the Founder lock the brand + the care-employee's name).

## Why this is on-thesis (and why it's NOT the parked self-serve SaaS)
- **The wedge:** the incumbents (Wellthy, Cariloop, Cleo, Torchlight…) all fled DTC for the employer channel because they're **human-concierge** businesses — human cost-to-serve can't be covered by an individual's price. yourco's AI-native model **removes that cost**, so the unit economics that killed DTC for them *work* for us. They can't follow us down without cannibalizing their human model. (Full analysis: `loops/advisor/2026-06-16_caregiving-os-dtc.md`.)
- **Moat reconciliation:** this is **operated, not self-serve.** The parked self-serve stance (`CLAUDE.md`) is about letting users *configure their own agent and absorb the eval risk* — that deletes the moat. yourco Care does the opposite: **yourco owns reliability + eval + approval; the consumer gets an outcome** and never touches models/infra. The moat *is* the product, productized for a consumer buyer. Consistent with "the client never touches tokens/models/infrastructure."

## What it is (the care employee)
A named, operated AI care-coordinator that handles the chaos for the family:
- **Care coordination** — appointments, meds, providers, the calendar, reminders.
- **Benefit & insurance navigation** — Medicare / Medicaid / VA: what the parent qualifies for, how to get it. *(Highest-value, most-confusing pain — likely the lead use case.)*
- **Family hub** — keep siblings aligned; shared status; expense tracking.
- **Documents & legal org** — records, POA, advance directives in one place.
- **24/7 intake** — the front desk for the parent's care.
- **Stage-based guidance** — "what do I do now" at each step of the journey.
- **Human escalation** — anything medical, a dosage, or a crisis routes to a human. Always.

## Hard guardrails (non-negotiable — care is high-stakes)
- **The AI never freelances medical advice, dosages, diagnoses, or crisis response.** Those are human-escalated or refused, by design. This is the approval gate at its strictest.
- **Rafi + Ray from day one** — PHI handling, duty-of-care/liability exposure, terms that make the "we coordinate, we don't practice medicine" line explicit. **Counsel reviews before launch.**
- **Honesty** — no fabricated benefit/eligibility claims; cite sources; "confirm with the provider/agency."
- **Privacy** — a vulnerable population's data; strict handling, consent, deletion.

## Pricing (Polo)
AI economics enable a price the human-concierge incumbents can't match — a low monthly subscription (Polo proposes the number + tiers; e.g. a base coordinator tier + a higher "navigation/concierge" tier). The whole pitch is *"the care coordinator you can finally afford — because it's AI, operated by yourco."* No number on the marketing site until Polo locks it (same standing rule).

## Go-to-market (lead DTC; how we crack the acquisition the incumbents couldn't)
- **Moment-of-need content + AEO** (Katie + Mario): own "mom can't live alone," "navigating Medicare for dad," "how do I care for an aging parent." This is where the exhausted adult child *is*.
- **Intent listening** (Sadie's engine, already built): caregiving forums / r/AgingParents / r/CaregiverSupport — same pipeline, a new vertical (added to `intent_verticals.json` as **"Caregiving"**). **Help-first, human-approved, never exploitative** — this population especially.
- **Partnerships** (the referral graph at the moment of need): hospital discharge planners, geriatric care managers, estate attorneys, senior-living.
- **Employer channel = later expansion** (B2B2C), not the lead — DTC AI-native is the unlock.

## Posture: validate as you build
the Founder's call is to launch it as an offering — so build it, but **prove the wedge as you go**: the one thing that must be true is *AI-native DTC acquires + retains profitably where human-concierge DTC couldn't.* Watch CAC + retention from the first cohort; the benefit-navigation use case is the likeliest hook. Don't let it pull focus from the core SMB launch (still pre-revenue, OtherVenture-gated) — sequence/staff deliberately.

## Owners
Kimi (delivery/build of the care employee) · Bella (a "care audit" intake could front it) · Polo (pricing) · Rafi + Ray (compliance/legal — gating) · Katie + Mario (acquisition content/AEO) · Sadie (intent) · Luka (brand + naming). the Founder approves the launch + the legal posture.

## Next steps (when greenlit to build)
1. Luka/the Founder: name the offering + the care employee.
2. Rafi + Ray: the compliance + terms posture (gating).
3. Polo: the DTC pricing tiers.
4. Kimi: spec the care-coordinator employee (the build).
5. Katie/Mario: the moment-of-need content + AEO plan; Sadie: caregiving intent keywords (added).
6. A landing page + a concierge-MVP first cohort to validate CAC/retention.
