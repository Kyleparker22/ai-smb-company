# Engagement Agreement — DRAFT TEMPLATE

> ⚠️ **Draft. Not legal advice. Counsel must review before use.** Fill every `[[ ]]`. Entity details from `finance/legal-docs/business-info.md`; fees from the agreed quote; scope from `clients/<client>/01_discovery.md`.
>
> ⚠️ **NOT YET COUNSEL-REVIEWED — added 2026-08-24 (for Ray):** §1.1 Change Orders · §1.2 what a
> retainer month buys · §3.1 the end-of-engagement handover · the widened AI-training restriction in
> §7 · the "hallucinations" wording in §9 · the SLA hook in §10 and `sla.md` itself. Drafted after reviewing a competitor's executed MSA+SOW
> (`decisions/2026-08-24_competitor-msa-teardown.md`). Structure and ideas only — no text was taken
> from that document. **§3.1 and the SOW's acceptance-credit remedy are the two that most need
> counsel eyes**, because both create obligations that outlast termination or touch fees.
>
> **Reconciled 2026-06-11 (Ray):** keeps the lean, model-specific terms (§1–8) and harvests the mature protective clauses (§9–17) from the imported `msa-v3-prior.md`. **Open architecture question for counsel:** keep this as a single Engagement Agreement, or split into a Master Services Agreement + per-engagement SOWs (better for repeat/expansion engagements — see `msa-v3-prior.md` for that structure). Drafted for the single-agreement model; easily re-split.

**This Agreement** is between **YourCo LLC**, a Florida limited liability company with a principal place of business at 123 Example St, Riverton, FL 33713 ("**YourCo**"), and **[[CLIENT LEGAL NAME]]** ("**Client**"), effective **[[DATE]]** (the "Effective Date").

---

## 1. What YourCo delivers
YourCo will design, build, deploy, and operate a named digital employee — **"[[EMPLOYEE NAME]]"** — inside Client's business to perform: **[[the use case, e.g. answer inbound calls/texts, qualify leads, book estimates, confirm, and log per the discovery doc]]**.
- **Go-live target:** a working employee on the first use case within **48 hours** of this Agreement being signed and Client providing the access listed in §4.
- **Optional audit (if elected):** a fixed-fee, one-week operational audit ending in a recommendation on the first employee to build. [[Included / not included]].

**1.1 Scope changes (Change Orders).** *(Added 2026-08-24 — counsel-gated; see the header note.)* The Services above,
plus any SOW, are the agreed scope. Either party may propose a change; a change to **scope, timeline, or
Fees** takes effect only when both parties sign a written **Change Order**. YourCo is not obligated to
perform work outside the signed scope until a Change Order is signed, and Client is not billed for it.
*Ordinary iteration is not a Change Order* — tuning prompts, adjusting a workflow, or improving the same
outcome is what the retainer buys (§2) and it happens in the weekly cycle. The test is whether the change
alters **what Client is paying for, or when they get it**. [[Counsel: confirm this test is workable — the
intent is a scope-creep valve that does not turn weekly iteration into paperwork.]]

**1.2 What a month of the retainer buys.** The build has a defined go-live (48 hours, above) with
acceptance criteria stated in the SOW. Past go-live, the retainer buys YourCo's **operation of the
employee and a prioritised queue of improvement each month** — not the completion of an unbounded list
within any one month. Where an SOW states a dated milestone, that date governs; otherwise remaining work
carries into the following month and Client may stop at any time under §3.

## 2. Fees
| Item | Type | Amount |
|------|------|--------|
| Audit (if elected) | Fixed, one-time | [[$ ]] |
| Build & implement [[Employee]] | Fixed, one-time | [[$ ]] |
| Run & manage (the retainer) | Monthly | [[$ ]]/mo |
| Each additional employee | Fixed build + retainer step-up | [[$ build / +$ /mo]] |

- The **build fee** is due **[[on signing / on go-live]]**. The **monthly retainer** begins **[[at go-live]]** and is billed **[[monthly, in advance]]**.
- **What the retainer covers:** operating the employee and *all* underlying infrastructure — model/token usage, voice, telephony, hosting, reliability, evals, watchdogs, and ongoing improvement. **Client is never billed for usage, tokens, models, or infrastructure** (see §6). Payment terms: **[[net 0 / on receipt]]**, **[[card / ACH]]**.
- **Late payments:** amounts not received within ten (10) days of the due date accrue interest at the lesser of 1.5%/month or the maximum permitted by law; YourCo may suspend the Services on an account more than fifteen (15) days past due after written notice and a five (5) day cure period. **Taxes** (sales/use/etc.) are excluded and are Client's responsibility, except taxes on YourCo's net income. Except as expressly stated, **Fees are nonrefundable**.

## 3. Term & renewal
- Initial term: **[[month-to-month / 3 months]]** from go-live, then **auto-renews monthly** unless either party gives **[[30]] days'** written notice. [[Counsel: confirm notice + auto-renew enforceability in target states.]]
- After the initial term, either party may terminate **for convenience** on 30 days' written notice; Client remains liable for Fees accrued through the effective date, including the notice period.
- The build is complete at go-live; the retainer is ongoing for as long as the employee runs.

**3.1 If the engagement ends — the handover.** *(Added 2026-08-24 — counsel-gated; see the header note.)* Because YourCo **operates**
the employee rather than handing over software, ending the engagement is a handover, not a switch-off. For
**[[30]] days** after the effective date of termination or non-renewal:
- YourCo **returns or deletes** Client data at Client's election, per the DPA (`dpa.md`), which controls.
- Client **keeps its own accounts, phone numbers, and tenant** — those were always Client's (§4) and were
  never YourCo's to withhold.
- YourCo provides Client's **configuration, prompts, and workflow documentation in human-readable form**,
  so Client or a successor can see exactly what ran and why.
- YourCo answers reasonable transition questions.

**What does not transfer:** YourCo's platform, eval frameworks, templates, and tooling (§5). The employee
stops running because it runs on YourCo's infrastructure — which is the same reason Client never received
a token, model, or infrastructure bill (§6). Say this plainly in the sale rather than at the exit.
[[Counsel: confirm whether transition assistance beyond the above should be fee-bearing, and whether the
[[30]]-day window is the right length.]]

## 4. What each party provides
- **Client provides:** timely access to the tools/accounts the employee needs (calendar, CRM, phone/number, brand assets), a named approver, and discovery input. Tenant/account access is granted by Client and may be revoked anytime.
- **YourCo provides:** the build, the infrastructure, reliability/eval/approval discipline, and weekly iteration.

## 5. Intellectual property
- **Client owns:** its own data, and the work product the employee produces *for Client* (the drafts, bookings, logs, communications).
- **YourCo owns:** its methods, templates (`yourco-template`), prompts, configurations, eval frameworks, and the underlying tooling and know-how — none of which are "work product." Client receives a non-exclusive, non-transferable **license to use the deployed employee** during the term.
- **Feedback:** any suggestions Client provides about the Services may be used by YourCo without obligation.
- **Residual rights:** YourCo may provide similar services to others (including in Client's industry) and may use the general knowledge, skill, and patterns it develops, provided no Client Confidential Information is disclosed.
- Neither party gets rights to the other's pre-existing IP.

## 6. Infrastructure & cost (the defining term)
YourCo absorbs and is solely responsible for all model, token, voice, telephony, and hosting costs of operating the employee. **Client will never receive a usage, token, model, or infrastructure bill.** Client pays only the fixed and retainer amounts in §2.

## 7. Data, security & confidentiality
- Each party keeps the other's Confidential Information confidential, using at least reasonable care, for the term plus **three (3) years** (trade secrets: for as long as they remain trade secrets). Standard exceptions apply (public, already known, independently developed, rightfully obtained). See also the separate **Mutual NDA**.
- YourCo handles Client data only as needed to operate the employee, applies commercially reasonable security, does not sell Client data, and **does not use Client data — or anything derived from it, including outputs — to train, improve, or otherwise enhance any foundation model or any general-purpose, multi-tenant, or multi-client model or system**, without Client's express prior written consent (and configures AI sub-processors to opt out of training + minimize retention). Personal data is governed by the **Data Processing Addendum** (`dpa.md`), which controls over this Agreement on data matters.

## 8. Approvals & human-in-the-loop
The employee **drafts and prepares**; anything customer-facing that Client designates as gated is **not sent without Client approval**. Go-live, anything touching Client's tenant/number, and material scope changes require Client sign-off. Client is responsible for reviewing AI outputs before relying on them and for final business decisions made in reliance on them.

## 9. AI output limitations
Client acknowledges that: (a) AI systems are probabilistic and may produce errors, omissions, misinterpretations, or confident-sounding fabrications (commonly called "**hallucinations**"); (b) YourCo does not guarantee the accuracy, completeness, or suitability of any specific AI output; (c) Client is responsible for reviewing and verifying outputs before relying on them; and (d) the Services augment, not replace, human judgment. YourCo is not liable for business decisions, lost opportunities, or outcomes resulting from AI outputs.

## 10. Representations, warranties & disclaimer
- **Mutual:** each party has the authority to enter into and perform this Agreement.
- **Services warranty:** YourCo will perform the Services in a professional and workmanlike manner consistent with industry standards. Client's **sole and exclusive remedy** for breach is re-performance of the non-conforming Services at no charge, if Client notifies YourCo in writing within thirty (30) days.
- **Service levels:** availability targets, severity-based response times, service credits, and the
  exclusions that go with them are in the **Service Level Agreement** (`sla.md`), which attaches to and is
  incorporated into this Agreement and **controls over this §10 on those subjects**. The SLA covers whether
  the employee is *running*; the SOW's acceptance criteria cover whether it is *working*. They are different
  promises and are measured separately. *(Added 2026-08-24 — counsel-gated; see the header note.)*
- **Client warranty:** Client has the rights/consents to provide Client data to YourCo, and Client's use of the Services complies with applicable law (including privacy law and Client's obligations to its own customers).
- **DISCLAIMER:** EXCEPT AS EXPRESSLY STATED, THE SERVICES ARE PROVIDED "AS IS" AND "AS AVAILABLE." YOURCO DISCLAIMS ALL IMPLIED WARRANTIES (MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE, NON-INFRINGEMENT) AND MAKES NO REPRESENTATIONS REGARDING REVENUE, COST SAVINGS, OR BUSINESS RESULTS.

## 11. Limitation of liability
- **No indirect damages:** to the maximum extent permitted by law, neither party is liable for indirect, incidental, special, consequential, or punitive damages, including lost profits, revenue, data, or goodwill.
- **Cap:** except for indemnification (§12), breach of confidentiality (§7) or the AI-training restriction, or a party's fraud or willful misconduct, each party's total cumulative liability will not exceed **three (3) times the total Fees paid or payable by Client in the twelve (12) months** before the event giving rise to the claim. [[Counsel: confirm cap multiple.]]
- These limits are an essential basis of the bargain.

## 12. Indemnification
- **YourCo** indemnifies Client against third-party claims that the Services, as provided and used per this Agreement, infringe a third party's IP — excluding claims arising from Client data, Client modifications, Client's combination with non-YourCo products, or Client's misuse.
- **Client** indemnifies YourCo against third-party claims arising from Client data (including unlawful collection or privacy violations), Client's misuse of the Services, Client's own business operations, or Client's failure to obtain necessary consents from its customers.
- Standard procedure: prompt notice, control of defense by the indemnifying party, reasonable cooperation.

## 13. Insurance
[[Once obtained]] YourCo will maintain commercial general liability, professional liability / E&O, and cyber liability coverage, and will provide certificates on Client's written request. [[Counsel/the Founder: confirm limits before representing coverage — do not state coverage that is not in force.]]

## 14. Dispute resolution & governing law
Governed by Florida law. The parties will first attempt informal resolution (15 days), then non-binding mediation in **Pinellas County, Florida**; unresolved disputes are resolved exclusively in the state and federal courts in Pinellas County, Florida. Either party may seek injunctive relief for breach of §5 (IP) or §7 (confidentiality) without first mediating. **The parties waive class actions and jury trial.** [[Counsel: confirm.]]

## 15. Publicity
YourCo will not use Client's name or logo externally without Client's prior written consent, but may reference the engagement on an **anonymized basis** (no name/logo/identifying detail) in case studies and methodology.

## 16. General
Independent contractors; no agency/partnership. Entire agreement (with the DPA + any SOW); the DPA controls on data matters. No assignment without consent (except to a successor in a merger/sale). Force majeure (excluding payment). Notices in writing (to YourCo: founder@yourco.example.com + the address above). No waiver unless written. Severability with reform. No third-party beneficiaries. Counterparts + electronic signatures are originals.

---

**YourCo LLC** — By: ______________  Name: the Founder  Title: Authorized Member  Date: ____
**[[CLIENT]]** — By: ______________  Name: [[ ]]  Title: [[ ]]  Date: ____

> Execute via DocuSign (the Founder approves the send + counterparty). Store the signed copy in `clients/<client>/`. **Counsel review required before first use.**
