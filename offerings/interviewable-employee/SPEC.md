# The Interviewable Employee — Build Spec

**Working name:** The Interviewable Employee (frontier #2)
**Author:** the Founder
**Stack:** Vapi (voice; locked platform, `decisions/2026-06-08_Reed-production-stack.md`) + Twilio · Claude API behind a **retrieval-gated** answer layer over the eval ledger (#4 schema) · demo-tenant ledger as the corpus · web fallback (text interview on the staged site) · transcripts → CRM lead capture
**Status:** Spec — see `offerings/_frontier-roadmap.md` row #2. Build trigger: **voice budget + first demo tenant.**
**Pillar / form factor:** Sales/Revenue (pillar 2) as yourco's own demand-gen surface; form factor 3 (embedded AI surface) wearing form factor 1's face (it presents as the employee being interviewed).

---

## 1. Concept

Before a prospect hires the digital employee, they **interview it** — by phone (Vapi) or on the site — and they interview it *about its own performance*. "How many intake calls did you handle last month?" "What's your error rate?" "Tell me about a time you got something wrong." "What happens when you don't know?" Every answer is grounded **only** in the agent's real eval record: the ledger rows behind it are the sole corpus, retrieved per question, cited in the transcript. Where no record exists, the agent says so — *"I don't have a record for that"* — because architecturally it has nothing else to say (§3). The interview closes the exact gap every AI vendor papers over with claims: the prospect doesn't have to believe our marketing; they cross-examine the evidence, conversationally, the same way they'd interview a human hire — including the question no human candidate answers honestly: "tell me about your failures." Ours answers from the incident log.

**Pre-revenue honesty is a design input, not a footnote.** Until client engagements generate client ledgers, the interviewable employee is the **demo-tenant** employee, and it says so in its own voice, unprompted, at the top of every interview: *"Everything I'll tell you comes from my evaluation record in yourco's demonstration environment — a real record of real runs, but not a paying client's operation."* Honestly-labeled demo evals beat fabricated production stats in exactly the sales conversations worth having; the label converts the constraint into credibility.

## 2. Why it's never been done

Every AI product demo is a scripted happy path; every AI vendor's stats page is marketing-authored. Nobody lets prospects free-range interrogate the product about its own failure record, for two structural reasons: (1) most vendors have no eval record to expose — the commodity tooling layer doesn't produce one; (2) those who have one can't let an LLM near a sales conversation unsupervised, because it will improvise flattering numbers — the fabrication risk is disqualifying without an architecture that makes fabrication impossible rather than discouraged. yourco has both missing pieces as standing infrastructure: the ledger exists as the moat layer's exhaust (one ledger, three windows — Trust Ledger #1 public, Invoice #4 per-client, this spec spoken aloud), and retrieval-gated generation with a refusal eval is precisely the reliability discipline the company sells. The interview *is* the moat, performed live: the demo isn't what the agent can do — it's that its claims are auditable.

## 3. Build shape

| Piece | What it is | Notes |
|---|---|---|
| Demo-tenant ledger | The #4 schema populated by real demo-tenant runs (intake calls handled, drafts produced, eval passes/fails, seeded-and-caught incidents, autonomy promotions) | Real runs, real records — the demo tenant is operated like a client; nothing hand-authored into the ledger |
| Retrieval-gated answer layer | Question → intent parse → **ledger query** → answer composed *only from returned rows*, row IDs attached → empty result set forces the no-record response. The generation prompt receives retrieved rows and conversation state, **no free background knowledge about performance** | The load-bearing component. Honesty enforced by architecture (closed corpus + citation requirement), not by prompt admonition |
| Fabrication eval (pre-launch gate + weekly) | Adversarial question bank (leading questions, flattery bait — "so you're basically 100% accurate?", stat-fishing for records that don't exist) → every answered claim machine-checked against cited rows; **any uncited quantitative claim = gate failure** | Kolby owns; the surface does not ship or stay live without a passing run |
| Voice surface | Vapi assistant + Twilio number; interview persona = candid candidate, not salesperson; ~10-min cap → warm close ("want to see me work on your business?" → audit CTA) | Reed's demo craft; ElevenLabs voice per stack |
| Text surface | Same answer layer embedded on the staged site ("interview the employee") | Ships first — no per-minute cost, same architecture proven cheaper |
| Capture loop | Transcript + interest signals → CRM lead (standard capture path); transcript emailed to the prospect on request (it's citations all the way down — send it proudly) | Approval-gated send per house rule |

**Data sources:** the demo-tenant eval ledger exclusively (later: a consenting client's ledger for their own expansion conversations — never cross-client). **Effort band:** M — answer layer + fabrication eval ~3–4 days; demo-tenant ledger accrues from operating the demo tenant (calendar time, not build time); Vapi wiring ~1–2 days on the locked stack.

## 4. Moat fit

The sharpest possible dramatization of proof-integration-trust: the prospect experiences the eval layer *as the sales pitch*. It is unfakeable by the no-code competition in the literal sense — an operator without a ledger cannot ship an interview grounded in one, and an interview grounded in nothing fails the first skeptical question. It bootstraps the flywheel's **Trust** stage pre-revenue using the one proof yourco owns outright (it runs on its own agents — the demo tenant is that fact, interviewable). The refusal behavior ("no record of that") is itself the demo of the house discipline that agents don't freelance. And every model upgrade makes the interview smoother at the same record-boundedness — the dividend, live on a phone call.

## 5. Gates / compliance

- **launch-gate:** this is a public-facing branded surface — **staged, internal-demo only until the gate clears** (`processes/launch-gate.md`). Usable immediately in within-gate contexts (screen-share demos, in-person per `decisions/2026-07-20_in-person-local-gtm.md`).
- **Credibility gate (hard):** no fabricated metrics — enforced by §3's architecture plus the fabrication eval as a launch gate. Demo-tenant provenance disclosed in-interview, on the surface's page copy, and in the transcript header. Any illustrative example in marketing copy for this offering is labeled illustrative.
- **AI disclosure:** the caller always knows they're talking to an AI (it's the premise, but stated anyway at pickup — also aligns with bot-disclosure law trendline).
- **Recording consent:** Florida two-party consent — transcript/recording only after in-call notice + affirmative consent; decline → interview proceeds, no retention beyond the session. Language rides the legal-suite/privacy review (**gates #1–2**, `processes/counsel-gates.md`); outbound calling is out of scope (inbound only — no TCPA surface).
- **Approval gates:** transcript sends and CRM-triggered follow-ups R1 per house rule (the Founder sends; agents draft). Agent-naming rule: the interviewable employee presents by **function** with a demo persona name that is *not* an internal roster name (external-surface rules).

## 6. Pricing frame *(assumption-stated; Polo locks)*

**Not a SKU — a conversion asset.** It's yourco's own top-of-funnel: cost is Vapi/Twilio per-minute + tokens (~single-digit $/interview, illustrative), justified against demo-to-audit conversion. Two priced descendants, both later: (1) inside a client engagement, the client's *own* agents become interviewable from their own ledger — folded into Suite-and-up retainers as a trust feature for the client's stakeholders (~$250–500/mo equivalent value if broken out; usually not broken out); (2) at expansion/renewal, the interview is the live rendering of the Self-Proving Invoice — priced nowhere, worth the renewal. All figures illustrative.

## 7. Activation trigger (build)

**Voice budget + first demo tenant** (roadmap: compounding era, "demo-tenant polish"). Sequenced entry: the **text surface can ship as soon as the demo-tenant ledger has ~4+ weeks of real records** (no voice budget required — same architecture, zero marginal cost), voice follows when the budget line opens. Prerequisite dependency stated plainly: this offering consumes the #4 ledger schema; the demo tenant starts writing that ledger the day the template hooks land.

## 8. What we will NOT do

- **No invented stats, structurally.** The answer layer has no path to a quantitative claim without a cited ledger row; the fabrication eval is a standing launch/stay-live gate. If the eval fails, the surface comes down — not gets a warning.
- **No demo-tenant numbers passed off as production.** Provenance disclosure is mandatory, in-voice, every interview, even after real clients exist (at which point client-record interviews are separate, consented surfaces). Cross-client data never mixes; no client's ledger is ever a sales prop for another prospect without written approval.
- **No cherry-picked corpus.** The interview corpus is the full demo-tenant ledger — incidents included. Curating failures out of the retrievable set is fabrication by omission and fails the same gate.
- **No pushy-sales persona.** The agent is a candidate being interviewed, caps its own pitch to the single closing CTA, and never pressures. It also never disparages named competitors — it answers about itself, from records.
- **No advice, no freelancing.** Questions outside the record ("should I fire my receptionist?", anything medical/legal/financial) get the refusal + human-handoff path, per the autonomy matrix regulated-advice row.
- **No public launch before OtherVenture clears, no recording without consent, no outbound dialing** — full stop, each per its gate above.
