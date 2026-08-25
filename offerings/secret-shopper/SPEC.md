# The Secret-Shopper Fleet — AI-as-customer experience audits (Frontier #6)

**Status: FULLY COUNSEL-GATED. No probe of any kind — no call, no form, no email — until the Rafi/Ray probe protocol (§5) clears counsel. This spec designs the offering and frames the legal questions; it authorizes nothing.**
**Roadmap row:** `offerings/_frontier-roadmap.md` #6 — "AI experiences the prospect's business as a customer; delivers the timestamped truth." Counsel batch: rides the existing one-engagement-across-gates counsel package (`processes/counsel-gates.md`).
**Owners:** Rafi (probe protocol + compliance posture) + Ray (counsel questions) + Bella (report → audit handoff) + the Founder (per-probe sign-off, always).

---

## 1. Concept

Before (or as the hook for) the Audit, yourco's AI experiences the prospect's business exactly as a customer does: calls the main line at 10am and 7pm, fills the website contact form, sends the "can you give me a quote?" email — then waits, timestamps everything, and compiles the experience report. *"Your phone rang out at 2:14pm Tuesday. Your web form's reply came 71 hours later. Your competitor answered in one ring."* No slide deck argues like a prospect's own missed calls do. The report is the single sharpest pre-audit door-opener yourco could own: not "AI could help you" but "here is, timestamped, what your customers experienced this week."

It also becomes a post-engagement proof surface: run the same probes after the OS goes live and the before/after is the outcome, self-documented (real numbers only — never projected, never fabricated).

## 2. Why this has never been done

- **Human mystery shopping doesn't scale down.** The incumbent industry serves chains and franchises with per-visit human shoppers; nobody mystery-shops a 12-person hardscaper — the unit economics fail, exactly the Wellthy/Cariloop pattern (cost structure flees the small buyer, AI-native removes the cost).
- **It requires being on both sides.** The report is only a door-opener if the prober can also *fix* what it finds. Pure audit shops can measure but not remediate; tool vendors can remediate but never probe (their product is the thing being tested). An operated-OS firm is the only shape where probe → diagnose → build → re-probe is one loop.
- **The compliance is genuinely hard** — recording law, deception bounds, AI-calling rules (§4–5). Doing this casually is a lawsuit; doing it rigorously requires exactly the compliance/eval/audit discipline that is yourco's moat layer. The barrier is the moat.

## 3. Build shape (small — mostly existing stack)

- **Probe channels:** voice (Vapi + Twilio — the locked voice stack, `decisions/2026-06-08_Reed-production-stack.md`), web forms (headless browser), email (probe-dedicated identity, never `yourco.com` primary sending domain). Each probe = a scripted, bounded scenario from an approved library (§5) — never improvised.
- **Probe ledger:** every probe pre-registered (target, channel, scenario ID, time) and post-logged (timestamped transcript-or-notes per counsel's ruling in §4, response latency, outcome). Append-only, git-tracked — the same audit-trail discipline as everything else in the OS. The ledger is both the compliance record and the report's raw material.
- **The report:** a white-label-quality one-pager per prospect — timeline of touches, response times, dropped threads, what a real customer would have done next. Feeds Bella's Audit directly (the probe findings pre-fill the bottleneck quantification). Report facts are the ledger's facts, verbatim — no extrapolation.
- **Fleet cadence:** batched probe windows (e.g. business hours + after hours × 2 channels) so one prospect costs minutes of runtime. Runs as a runtime loop only after protocol clearance; starts fully manual, per-probe the Founder-approved (R1 — see §5).

## 4. THE COMPLIANCE PROTOCOL (the centerpiece — counsel decides, this spec decides nothing)

**4a. Florida recording law — the threshold question.** Florida is an all-party-consent state for recording oral communications (Fla. Stat. §934.03): recording a call without every party's consent is a felony-grade exposure, and yourco is Florida-based with Florida-first prospects. **Therefore: no call recording, period, under any probe design, until counsel rules.** The design options to PRESENT to counsel — decide nothing here:
1. **Notes-only:** the agent retains no audio and no verbatim transcript; it writes structured contemporaneous notes (times, outcome, latency, summary). Safest posture; weakest evidence artifact. Is a summary note free of §934.03 exposure?
2. **Agent-as-party transcription:** no audio retained; the AI agent — itself a party to the call — produces a real-time transcript. Is machine transcription without audio retention an "interception/recording" under §934.03? This is the sharpest question for counsel; do not assume the answer is no.
3. **Disclosed recording:** open with "this call may be recorded" (as businesses themselves do). Lawful, but does disclosure destroy probe realism, and does the *prospect's own* "calls recorded" greeting constitute the needed consent posture for our side?
4. **Jurisdiction-split design:** voice probes only where counsel confirms one-party rules apply; forms/email everywhere (no oral communication → different analysis; confirm no separate wiretap/stored-comms issue).

**4b. AI-calling law.** Do outbound AI-voice probe calls to business lines implicate TCPA/FTSA (AI/prerecorded-voice and autodialer rules — note counsel gate #4 already tracks FTSA/TCPA for SMS)? Business-to-business call exposure, required disclosures that a voice is AI, and Do-Not-Call interplay: counsel maps it before any voice probe.
**4c. Deception bounds.** Mystery shopping is a lawful, established practice — but its lawful envelope is what counsel must draw for an AI doing it. Present the intended posture: fictitious-but-ordinary customer persona, ordinary inquiries only. Never: impersonating a real person, fake emergencies, probing regulated/professional services under false pretenses, protected-class test scenarios, inducing a binding transaction, or collecting anything beyond the business's ordinary public-facing responses.
**4d. Data handling.** Probe artifacts contain the prospect's staff voices/names/replies — collected before any engagement exists. Retention window, storage isolation, and whether the report may be shown to the prospect's *competitor* (answer we propose: never — one probe, one prospect, its report goes only to them) all go in the counsel package.

## 5. Gates (nothing fires without all four)

1. **Counsel clearance** of the §4 package — rides the existing counsel batch; Ray drafts the questions from §4 verbatim; row to be added to `processes/counsel-gates.md` when the package goes out.
2. **The Rafi/Ray probe protocol** — the standing document (to be written post-counsel, encoding counsel's rulings): approved scenario library, channel rules per jurisdiction, disclosure scripts, retention rules, the pre-registration requirement. **No probe of any kind before this protocol exists and is counsel-blessed** — including "harmless" form fills.
3. **Per-probe sign-off:** every probe batch pre-registered and the Founder-approved (R1). Probing is external, deceptive-by-design contact — under the Autonomy Matrix hard rule it starts gated and its *ceiling* is a counsel + protocol question, not an eval question alone.
4. **launch-gate:** probes are external contact by yourco; the master external gate (`processes/launch-gate.md`) applies on top of everything above.

## 6. Moat fit

Compliance-heavy probing done rigorously — protocol, pre-registration, audit ledger, jurisdiction logic, eval on probe quality — is the moat layer pointed outward. Any operator can place a sneaky call once; nobody undisciplined can run a *defensible fleet* of them. And the probe→build→re-probe loop only exists for a firm that operates the fix: the report's before/after becomes Trust-Ledger-grade outcome proof (real timestamps, real deltas, no fabrication).

## 7. Pricing frame

The probe report is a **door-opener, not a SKU**: free as the pre-audit hook. (Since 2026-08-16 the Audit itself is free, so there is no price to fold it into — the probe is simply the first thing the prospect gets.) When it converts (Bella's diagnosis starts pre-loaded with probe evidence). Post-engagement re-probes are included proof-of-outcome inside the operated retainer. Polo owns whether a standalone "experience report" price ever exists; default is no — selling the report without the fix invites pure-audit positioning, which is not the business.

## 8. Activation trigger

Counsel clearance of the §4 package + the Rafi/Ray protocol written and blessed + OtherVenture clear. Until all three: **zero probes.** Build work permitted meanwhile: scenario-library drafting, report template, probe-ledger schema — words and files, no contact.

## 9. What we will NOT do

- **No probe before the protocol** — not one call, form, or email, "just to test the plumbing." Plumbing tests run against yourco-owned surfaces only.
- **No call recording absent explicit counsel clearance** of a specific §4a option.
- **No deception beyond the ordinary-customer envelope** (§4c list is absolute).
- **No probing current clients' businesses** without their written knowledge in the engagement terms — clients are partners, not targets.
- **No selling A's probe report to B** (or to anyone but the probed business), and no cross-prospect "rankings."
- **No real-person impersonation, ever** — synthetic persona only (and no implication any real person reviewed/endorsed anything — house rule).
- **No autonomous probing:** the fleet's cadence can scale; the per-batch human sign-off does not get evaled away — R1 by design until counsel + protocol explicitly say otherwise.
