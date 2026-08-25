# Business Associate Agreement (BAA) — DRAFT TEMPLATE

> ⚠️ **Draft. Not legal advice. Counsel must review before use.** Required whenever an engagement has YourCo handling **Protected Health Information (PHI)** on behalf of a HIPAA-covered entity (dental, medical, therapy, vet, and similar). Attaches to the Engagement Agreement + DPA; **controls over both on PHI matters.** Owner: Rafi (with Ray + counsel). Trigger: discovery flags "is this PHI?" → this BAA must be signed **before any PHI flows** (a hard go-live gate). Fill every `[[ ]]`.

**This BAA** is between **[[CLIENT]]** ("**Covered Entity**") and **YourCo LLC** ("**Business Associate**"), effective **[[DATE]]**, and forms part of the Engagement Agreement. Terms not defined here have the meaning given in **HIPAA** (the Health Insurance Portability and Accountability Act, the HITECH Act, and 45 CFR Parts 160 and 164).

## 1. Definitions
- **PHI / ePHI** — Protected Health Information (electronic PHI) as defined at 45 CFR 160.103, limited to PHI that YourCo creates, receives, maintains, or transmits **for the Covered Entity** under the engagement.
- **Breach, Security Incident, Required by Law, Designated Record Set, Subcontractor** — as defined in HIPAA.
- The **Privacy Rule** (45 CFR Part 164, Subpart E) and **Security Rule** (Subpart C) apply to YourCo as a Business Associate to the extent set out below.

## 2. Permitted uses & disclosures
YourCo may use/disclose PHI **only**: (a) to perform the services in the engagement (operating the named digital employee — e.g. intake, scheduling, logging); (b) as Required by Law; and (c) for YourCo's proper management and administration, provided any disclosure for that purpose is Required by Law or made under written assurances of confidentiality + breach-notice from the recipient. YourCo will **not** use or disclose PHI in any manner that would violate the Privacy Rule if done by the Covered Entity, and will limit uses/disclosures to the **minimum necessary**.

## 3. YourCo's obligations
- **Not use or disclose** PHI other than as permitted by this BAA or Required by Law.
- **Safeguards** — implement appropriate **administrative, physical, and technical safeguards** (and, for ePHI, comply with the Security Rule, 45 CFR 164.308/310/312/316) to protect PHI. YourCo's measures are tracked in `processes/compliance-posture.md` (encryption in transit/at rest, least-privilege + MFA, secrets isolated, approval gate on external/destructive actions, monitoring). **No clinical advice or decision-making** by the digital employee.
- **Minimum necessary** — request, use, and disclose only the minimum PHI necessary.
- **Report** to the Covered Entity any use/disclosure not permitted, any **Security Incident**, and any **Breach of Unsecured PHI** — **without unreasonable delay and no later than [[5]] calendar days** of discovery (well inside HIPAA's outer limit), via the Security Incident Runbook (`agents/rafi/security-incident-runbook.md`), with the breach details HIPAA requires.
- **Subcontractors / sub-processors** — ensure any Subcontractor that creates/receives/maintains/transmits PHI agrees in writing to **restrictions and conditions at least as protective as this BAA** (flow-down BAAs). YourCo remains responsible for them.
- **Individual rights** — make PHI in a Designated Record Set available to the Covered Entity (or the individual) for **access** (164.524) and **amendment** (164.526), and provide an **accounting of disclosures** (164.528), within the timeframes the Covered Entity reasonably specifies.
- **HHS access** — make YourCo's internal practices, books, and records relating to PHI available to the Secretary of HHS for determining the Covered Entity's compliance.
- **Carry out** any of the Covered Entity's Privacy Rule obligations that YourCo has agreed to perform, in compliance with the Privacy Rule.

## 4. Covered Entity's obligations
The Covered Entity will: notify YourCo of any limitation in its Notice of Privacy Practices, any restriction on use/disclosure the individual has agreed to, and any changes to or revocation of authorization, to the extent these affect YourCo's use/disclosure; and **not** ask YourCo to use/disclose PHI in any manner that would violate the Privacy Rule if done by the Covered Entity.

## 5. Term & termination
- **Term:** effective on the date above; continues while YourCo holds PHI for the Covered Entity.
- **Termination for cause:** on the Covered Entity's notice of a material breach by YourCo that YourCo fails to cure within **[[30]] days**.
- **On termination:** YourCo will **return or destroy all PHI** it holds (and ensure Subcontractors do), and retain no copies, **except** where return/destruction is infeasible — in which case YourCo extends the BAA's protections to that PHI and limits further use/disclosure to the reasons that make return/destruction infeasible. Provisions that by nature survive, survive.

## 6. General
No third-party beneficiaries. The parties will **amend** this BAA as needed to comply with changes in HIPAA. Any ambiguity is **resolved to permit compliance with HIPAA**. This BAA controls over the Engagement Agreement + DPA on PHI matters. Liability is subject to the Engagement Agreement's limitation of liability, except where HIPAA provides otherwise.

---
**[[CLIENT]] (Covered Entity)** — By: ______ Name: ______ Title: ______ Date: ____
**YourCo LLC (Business Associate)** — By: the Founder, Authorized Member  Date: ____

> Execute alongside the Engagement Agreement + DPA (DocuSign). **Counsel review required before first use.** Must be signed **before any PHI flows.**
