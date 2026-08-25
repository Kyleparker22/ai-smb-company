# The Understudy Program — Build Spec

**Working name:** The Understudy Program (frontier #7)
**Author:** the Founder
**Stack:** golden client template overlay · Claude API (pattern extraction, handbook drafting) · client tenant email/calendar via Graph or Google Workspace API (scoped, read-only in shadow mode) · the standard moat layer (eval · approval · audit log)
**Status:** Spec — see `offerings/_frontier-roadmap.md` row #7. Build trigger: **first signed client** (the natural audit upsell).
**Pillar / form factor:** Company Brain (pillar 7), shipped as form factor 1 (a named digital employee) with a permanent form-factor-2 shadow loop underneath.

---

## 1. Concept

Quit-proofing as a product. Every SMB has two or three humans whose sudden absence would stop the business — the office manager who is the only one who knows how billing really works, the estimator whose pricing logic lives in his head. The Understudy is a **shadow agent per key human role**: with the client's and the employee's documented consent, it gets scoped read access to that role's exhaust — email patterns, calendar rhythm, the workflows they actually run, the decisions they make and how — and continuously maintains a **living role handbook**. When the person quits, gets sick, or takes a vacation, the understudy **steps in approval-gated**: it drafts what the role would have produced, routed to whoever the client names, until a human backfills or returns.

The frame is existential, and it's the frame the audit already surfaces: the audit's bottleneck analysis routinely finds "this entire function is one resignation away from stopping." Today the answer is a shrug. The Understudy makes it a line item.

**Two products in one, deliberately ordered:** (1) the **handbook** — a durable, human-readable, client-owned artifact that de-risks the role even if the agent is never activated; (2) the **agent** — the same knowledge made operational on an absence event. The handbook is the primary deliverable. A client who cancels keeps the handbook; quit-proofing survives the engagement. This ordering is what makes the offer honest rather than "we'll replace your people" (we won't, and we say so).

## 2. Why it's never been done

Insurance products exist for key-person *death* (key-man life insurance pays money, replaces nothing). Documentation consultants write SOPs that are stale the month after the engagement ends. Neither continuously observes the role, and neither can *act* in it. What's new is the combination AI-native operators can now deliver: continuous low-cost observation of a role's real exhaust + a handbook that never goes stale because a loop maintains it + a standby actor whose activation is safe because it runs on an earned-autonomy reliability layer. No-code operators can't ship the third part (activation without the moat layer is a liability, not a product), and staffing/insurance incumbents can't ship the first two. The window exists because the moat layer exists.

## 3. Build shape

| Piece | What it is | Notes |
|---|---|---|
| Consent + scoping pack | Signed role-owner consent, access-scope schedule (which mailboxes/calendars/systems, read-only), exclusion list (personal folders, HR/medical threads) | Template doc; per-role checkbox schedule. Nothing connects until signed. |
| Shadow loop | Scheduled (weekly) headless run: reads the period's exhaust in scope → extracts patterns (recurring workflows, decision rules, contacts, cadences, vocabulary) → diffs against the handbook → proposes handbook updates | R0 observe-only, permanently. Runs on the standard runtime loop pattern (`.claude/skills/add-runtime-loop`). |
| The role handbook | `clients/<client>/understudy/<role>-handbook.md` — living doc: responsibilities, recurring workflows step-by-step, decision rules with observed examples, key contacts + tone notes, calendar rhythm, systems + access map, "what only this person knows" open-questions list | Human-readable first; the agent reads the same file. Client-owned, exportable. |
| Interview supplement | Quarterly structured interview (async questionnaire or call) to capture what exhaust can't show — tacit judgment, the why behind decision rules | The open-questions list drives it. |
| Activation runbook | Named activation events (resignation, illness, PTO ≥ X days — client defines), named approver, scope of what the understudy covers vs. escalates | Activation is a client decision, never automatic. |
| The active understudy | On activation: a named digital employee (client-branded name, its own mailbox in the client's tenant) working from the handbook, **R1 draft-for-review** on everything outward | Deactivates on return/backfill; writes a handover debrief. |

**Data sources:** client-tenant email + calendar (read-only, scoped), the systems the role touches (read-only where APIs permit), the quarterly interview. **Effort band:** M — the shadow loop and handbook schema are template-generic (build once, ~3–5 focused days into `_yourco-template`); per-role onboarding thereafter is S (consent pack + scope wiring + first-pass handbook, ~1 day/role).

## 4. Moat fit

- **Proof:** the handbook is auditable evidence of coverage; the shadow loop's eval is "did the handbook predict what the role actually did this month?" — a measurable drift check (Kolby's weekly pass).
- **Trust:** this product is *made of* executive trust — an owner grants an agent standing read access to a key employee's mailbox only to an operator with a demonstrated approval/audit posture. No-code can't be handed this.
- **Autonomy matrix, exactly:** shadow = R0 (inherently safe, forever); active = R1 floor on all external actions, climbing per the standard evidence rule *only within an activation window*. High-stakes role actions (pricing, payments) stay R1 by design.
- **Model-upgrade dividend:** better models read exhaust better → the handbook gets sharper at the same price. The standing obsolescence answer applies verbatim.
- **Expansion engine:** roles are the natural expansion unit — land one understudy, the audit's org map names the next two. Feeds Exit-Asset OS (#3) directly: understudied roles are documented owner-independence.

## 5. Gates / compliance

- **Employee consent is a hard precondition** — written, per-role, revocable; no covert monitoring, ever (see §8). Client attests it has authority under its own policies to grant the access.
- **Counsel gate (rides #1, `processes/counsel-gates.md`):** employee-monitoring consent language + the access-scope schedule join the engagement-agreement legal suite review. Florida is a two-party-consent state: **no call recording/transcription in scope v1** — exhaust means written artifacts + calendar only until counsel clears a recording posture.
- HR/medical/personal content is excluded by scope filter *and* by prompt-level refusal; anything ambiguous is dropped, not summarized. Heavy-PII handling per house standard (tenant-isolated, audit-logged, retention defined; delete exhaust extracts on role-owner revocation — the handbook keeps only the operational patterns).
- Approval gates on anything outward while active (R1); white-label — the understudy carries the client's brand and a client-chosen name, never "yourco" and never an yourco roster name (external-surface rules).

## 6. Pricing frame *(assumption-stated; Polo locks before first proposal)*

Priced as a Company Brain module on the standard bands: **~$2–4k setup per role** (consent pack, scope wiring, first-pass handbook + interview) **+ ~$500–1,000/mo per shadowed role** (the loop, handbook maintenance, quarterly interview, standby readiness). **Activation is included, not an emergency surcharge** — charging extra at the moment of crisis poisons the trust the product is made of; activated months may step up to the role's active band (~$1,500–2,500/mo) only while active, stated in the agreement up front. Multi-role bundles fold into OS-level pricing. All figures illustrative until first-ten-clients evidence.

## 7. Activation trigger (build)

**First signed client.** Offered as the audit upsell — the audit already produces the key-person risk map, so the pitch is one page pointing at the client's own org chart. Template pieces (handbook schema, shadow-loop prompt, consent pack) may be built into `_yourco-template` pre-signing per roadmap sequencing rule #8-adjacent (hooks predate clients); no per-client work before a signature.

## 8. What we will NOT do

- **No covert monitoring.** No shadow without the role-owner's own signed consent; consent revocation stops the loop same-day. We decline the engagement variant where the owner says "don't tell them."
- **No surveillance analytics.** The exhaust is never used for productivity scoring, performance review input, or "what is this employee doing all day" reporting — and we put that in the consent doc so the employee reads it too. The product is continuity, not oversight; one use of it as surveillance kills every future consent conversation.
- **No replacement marketing.** Never pitched or activated as a way to eliminate the human's job while they hold it. The understudy activates on absence events only.
- **No autonomous stand-in.** An active understudy never exceeds R2, and never on payments, pricing commitments, HR matters, or legal/medical/financial substance (R1 draft-for-review, standard matrix rule).
- **No call/voice capture** until the FL two-party-consent posture is counsel-cleared.
- **No fabricated coverage claims.** "Quit-proof" is the product name, not a guarantee; external copy states what is covered (documented workflows, drafted continuity) and what is not (tacit judgment not yet captured — the handbook's open-questions list is shown, not hidden).
- **No yourco branding or agent-roster names** on anything the client's staff or customers see.
