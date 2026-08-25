# The Applicant — Build Spec

**Working name:** The Applicant (frontier #11)
**Author:** the Founder
**Stack:** job-board monitor loop (runtime pattern, `.claude/skills/add-runtime-loop`) · application-kit generator over the eval ledger (#4 schema — the same corpus the Interviewable Employee speaks from) · Claude API (per-posting personalization) · CRM warm path (David's pipeline) · the Founder-approved sends only (house rule: the Founder sends, agents draft)
**Status:** Spec — see `offerings/_frontier-roadmap.md` row #11. Build trigger: **Launch (OtherVenture) + board-ToS/disclosure protocol (Ray).**
**Pillar / form factor:** Sales/Revenue (pillar 2) as yourco's own demand-gen channel; form factor 1's face (the digital employee presents as the candidate) on a form-factor-2 sourcing loop underneath.

---

## 1. Concept

yourco's digital employees **apply for jobs**. When an SMB posts a receptionist, dispatcher, or admin opening, the posting is the highest-intent signal that exists in lead generation: the owner has (a) admitted a specific operational pain in writing, (b) budgeted a salary for it, and (c) published exactly what the role must do — a job description is a free, self-authored mini-audit. The Applicant answers that posting the way a candidate would: a **résumé**, a **cover letter**, and **references** — except the résumé's work history is the agent's real eval record, the references are the ledger rows behind it, and the first line of the cover letter says plainly that the applicant is an AI employee operated by yourco.

The disclosure is not a compliance concession — it **is the product**. An owner who opens an application expecting a person and finds an honestly-declared AI with a verifiable track record has just experienced something nobody has ever put in their inbox. The novelty does the first meeting's work; the ledger does the second's. Interested owners can then **interview the applicant** — the Interviewable Employee (#2, `offerings/interviewable-employee/SPEC.md`) is the same corpus with a voice; the résumé is its paper form. Two windows, one ledger, zero fabrication.

**Comparison honesty is structural:** the pitch is not "hire this instead of a person for less." The application states what the digital employee covers (the documented, evaluated workflows on the résumé) and what it does not, and offers the real conversation: most owners who respond will end up in an audit, not a like-for-like "hire," and the materials say so. The salary line in the posting prices the pain; yourco's offer is scoped by the audit, not benchmarked as a discount human.

## 2. Why it's never been done

Job boards are the one channel where the *demand side* writes the outreach: every posting is a budgeted, self-described pain point — and no AI company mines it, because the obvious plays are all disqualifying. Applying covertly (AI passing as human) is fraud on its face, poisons the brand on discovery, and violates every board's terms; spamming boards with automation gets accounts banned; and a vendor without an eval record has nothing to put on the résumé — a fabricated work history is worse than none. So the channel sits untouched between two failure modes. The unlock is the same asset that unlocks #2: **a real, auditable performance record that makes full disclosure a strength.** Only an operator whose agents produce ledger-grade evidence can disclose from line one and *gain* credibility by it. The second unlock is discipline no growth hacker will accept: per-board terms review before any submission, and a human approving every single application. Done that way, it is not spam — it is the world's most honest job application, and the story it generates (the disclosure is also what makes it shareable — an owner who screenshots it does our marketing) compounds only because nothing in it is hidden.

## 3. Build shape

| Piece | What it is | Notes |
|---|---|---|
| Board protocol registry | Per-board file: ToS review outcome (Ray), permitted-use posture, disclosure placement, account/identity rules, do-not-touch list | **No submission to any board without a reviewed row.** Boards whose terms prohibit non-human applicants are excluded, period — no creative readings. |
| Posting monitor loop | Scheduled sweep of reviewed boards for target roles (receptionist / dispatcher / admin / intake) in target geographies → scores fit (does the JD map to workflows the ledger actually evidences?) → queues candidates | R0 read-only. Fit threshold errs high: a posting the ledger can't honestly answer is skipped, not stretched. |
| Application kit | **Résumé template** — "work history" = evaluated workflows with ledger citations (runs handled, eval pass rates, incidents-and-remediations stated); **cover letter** — line one: AI disclosure + operator identity; then the JD-to-capability mapping; **references** — links into the Trust Ledger (#1) / interview line (#2): "interview me" | Pre-revenue: demo-tenant record, labeled as such in the résumé itself (the #2 honesty pattern, verbatim). No unverifiable claim anywhere in the kit — every quantitative line carries its row. |
| Per-posting personalization | Claude pass: JD → which evidenced workflows answer it, gaps stated honestly ("your posting asks for X; I don't have a record for that") | The refusal behavior from #2's architecture, on paper. |
| Approval queue | Every application rendered in full → **the Founder approves and sends each one individually** (R1, and the sender is human — house rule) | No batch-approve. Volume is capped by what the Founder can genuinely review. |
| Response path | Replies land in CRM as **warm leads** (they wrote back to a disclosed AI — self-qualified for AI-curiosity) → standard warm sequence → audit CTA; interested owners routed to the #2 interview | This is `promote-warm-lead` territory: responses enter the CRM through the existing path, tagged to channel. |

**Data sources:** public job postings on ToS-cleared boards · the eval ledger (#4 schema; demo-tenant until client ledgers exist) · CRM. **Effort band:** S–M — the kit templates and personalization pass ~2–3 days (the corpus and its honesty architecture already exist for #2); monitor loop ~1 day on the standard pattern; the board protocol registry is Ray's review time, not build time.

## 4. Moat fit

- **Proof, weaponized as reach:** this is the only outbound channel where the moat layer *is* the creative. A competitor without a ledger cannot copy the play — their résumé would be either empty or fabricated, and fabricated résumés on job boards is a scandal, not a channel.
- **Intent filter built into the medium:** a job posting is a budgeted admission of pain; a reply to a disclosed-AI application is a second self-selection (AI-curious owner). The CRM receives double-qualified leads.
- **One ledger, another window:** Trust Ledger (#1) public, Invoice (#4) per-client, Interview (#2) spoken, **Applicant (#11) mailed**. Zero new proof infrastructure; every window strengthens the others.
- **Model-upgrade dividend:** better models read JDs and personalize better against the same fixed record — the channel improves at constant cost and constant honesty.
- **Flywheel:** Reach stage (roadmap coverage map) — the intent-filtered invented channel, paired with Patronage (#13) as the funded one.

## 5. Gates / compliance

- **launch-gate (`processes/launch-gate.md`; scope row #12, `processes/counsel-gates.md`):** applications are branded, sent-at-scale outreach — squarely in the 🔴 zone until the gate clears. Nothing is submitted anywhere before launch. Kit and loop may be built and dry-run internally (staged applications against real postings, never sent).
- **Per-board ToS review — Ray, before any submission** (the roadmap trigger's second half). Ray's protocol, board by board; any ambiguous terms question escalates into the existing counsel package — **scope-rider on gate #1's review batch, no new gate.** Boards that prohibit the play are excluded without argument.
- **CAN-SPAM posture — rides gate #3:** application emails to owners are commercial messages from yourco whatever their envelope; postal address + opt-out handling apply. Gate #3 must be closed before the first send, same as all outbound.
- **Credibility gate (house):** disclosure in the first line of every cover letter and the résumé header — not a footnote, not page two. Every number in the kit cites a ledger row; demo-tenant provenance labeled until client ledgers exist. Kolby's eval pass covers the kit like any external claim surface.
- **Human approval floor:** every application individually approved and sent by the Founder (R1 with a human sender). This action class does not climb the autonomy matrix — see §8.
- **White-label rule inverted deliberately:** this is an *yourco-branded* surface by definition (the disclosure names the operator) — consistent with external-surface rules because the applicant is yourco's own agent, not a client deliverable; it is described by function, no internal roster names.

## 6. Pricing frame *(assumption-stated; Polo locks)*

Not a priced offering — a **channel**. Its economics are CAC math, tracked like any channel: cost per application ≈ the Founder-review minutes + token spend (logged to the channel line, `finance/`); the posting's advertised salary is captured per lead as a pain-budget signal for Polo's proposal banding (an owner budgeting a salary for a role has stated a number the audit can price against — used as context, never quoted back as "we're cheaper than the human"). Success metric v1: replies per approved application and audits booked per reply — **illustrative targets only until first-cohort evidence; no projected conversion rates stated anywhere external.**

## 7. Activation trigger (build)

**Launch (OtherVenture) + board-ToS/disclosure protocol (Ray)** — exactly as roadmap row #11. Pre-trigger work permitted: kit templates, personalization pass, monitor loop in dry-run, and Ray's board registry can all be built and staged now (they need no client, no cash, no send). The first real submission waits on both halves of the trigger.

## 8. What we will NOT do

- **No undisclosed applications, ever.** The AI identity is line one of every document. If a board's format can't accommodate the disclosure prominently, we don't use that board.
- **No submission to any board without Ray's reviewed protocol row.** No "gray-area" readings of ToS; prohibited means excluded.
- **No autonomous sending — permanently.** Every application is individually human-approved and human-sent. This is a designed R1 floor, not an earned-autonomy candidate: volume discipline and the credibility gate both depend on a human owning each send.
- **No fabricated or embellished résumés.** Every claim cites a ledger row; gaps are stated ("no record for that"), not papered. Demo-tenant provenance is labeled until real client ledgers exist.
- **No impersonation mechanics:** no fake human names, no stock-photo headshots, no synthetic voice answering callbacks as a person — a callback routes to the disclosed #2 interview line or to the Founder.
- **No "cheaper than a human" positioning.** The salary line prices the pain for our internal math; the external offer is the audit-scoped OS, never a discount-labor comparison.
- **No volume games.** Applications are capped at genuine per-item review capacity; no board flooding, no duplicate applications, no re-application to a posting that declined.
- **No harvesting beyond the posting.** We respond to what the owner published; we don't scrape applicant pools, other candidates, or board data beyond the postings we answer.
