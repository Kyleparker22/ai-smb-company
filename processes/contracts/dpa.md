# Data Processing Addendum (DPA) — DRAFT TEMPLATE

> ⚠️ **Draft. Not legal advice. Counsel must review before use.** Forms part of the Engagement Agreement (`engagement-agreement.md`); controls over it on data matters. Fill every `[[ ]]`. Owner: Rafi (with Ray + counsel). Use when an engagement has yourco processing the Client's personal data.
>
> **Reconciled 2026-06-11 (Rafi + Ray):** upgraded from the lean draft to the depth of the imported `dpa-v3-prior.md` (definitions, state privacy laws, 72-hour breach clause, security annex, retention, DSR, audit), adapted to the Engagement Agreement model with the **current** sub-processor stack.

**This DPA** is between **[[CLIENT]]** ("**Controller**" / "**Business**") and **YourCo LLC** ("**Processor**" / "**Service Provider**"), and forms part of the Engagement Agreement dated **[[DATE]]**. Capitalized terms not defined here have the meaning given in the Engagement Agreement.

## 1. Definitions
- **Personal Information** — information within Client Data that identifies or is reasonably capable of being associated with a particular individual (names, business contact info, communication content, identifiers).
- **Data Subject** — the individual to whom Personal Information relates.
- **Processing** — any operation on Personal Information (collection, storage, use, disclosure, transmission, erasure, etc.).
- **Privacy Laws** — all applicable laws, including the **Florida Information Protection Act**, **CCPA/CPRA** (California), **VCDPA** (Virginia), **CPA** (Colorado), and other U.S. state privacy laws, as amended.
- **Security Incident** — any unauthorized access to, acquisition, use, disclosure, alteration, or destruction of Personal Information processed by yourco in connection with the Services.
- **Subprocessor** — any third party engaged by yourco to process Personal Information for the Services.

## 2. Roles
The Client is the **Business / Controller**; yourco is the **Service Provider / Processor** acting on the Client's documented instructions. Each party complies with its obligations under applicable Privacy Laws.

## 3. Scope & purpose
- **Data subjects:** the Client's personnel; and the Client's customers, leads, and counterparties whose information appears in materials the Client shares or that the employee processes.
- **Categories:** business contact identifiers; communication content; operational/project data; technical metadata (timestamps, AI interaction logs).
- **Purposes:** operating the named digital employee; configuring/testing/running AI agents and automations; producing deliverables; aggregated, de-identified service improvement (§5); legal compliance; enforcing the Agreement.
- **Duration:** the term of the engagement, plus the retention in §8.

## 4. yourco's obligations
- Process Personal Information **only on the Client's documented instructions**, except where law requires otherwise.
- **Do not sell or share** Personal Information; do not retain/use/disclose it outside the direct business relationship or for any purpose other than the Services.
- **Do not combine** Client Personal Information with data from other sources except as needed to provide the Services.
- Bind personnel and contractors to **confidentiality**; apply the security measures in §7.
- Notify the Client promptly if yourco can no longer meet its Privacy-Law obligations.

## 5. Aggregated data & AI model use
yourco may create and use **aggregated, de-identified** data for internal quality improvement, provided it cannot reasonably re-identify the Client or any Data Subject and does not attempt to. **yourco will not use Personal Information to train foundation AI models** and will not share it with AI sub-processors for training their general-purpose models; where providers offer it, yourco exercises **training opt-outs** and minimizes retention.

## 6. Sub-processors
The Client gives general written authorization for yourco to engage sub-processors. Current authorized sub-processors (maintained against `processes/compliance-posture.md`; voice-stack applies to voice engagements only):

| Sub-processor | Function | Location |
|---|---|---|
| Anthropic, PBC | Primary LLM API (AI agents/automations) | US |
| Hostinger International Ltd. | Cloud infrastructure (runtime hosting) | US/EU |
| Google LLC (Workspace) | Business email, calendar, document storage | US |
| Slack Technologies, LLC | Team communication / any Client-shared channels | US |
| Vapi, Inc. · Twilio Inc. · ElevenLabs, Inc. | Voice agent, telephony, voice synthesis (**voice engagements only**) | US |
| Stripe, Inc. *(or designated processor)* | Payment processing (fee collection only; no Data Subject PI) | US |

yourco keeps a current list available on request, and gives the Client **at least 30 days'** notice of any new/replacement sub-processor that will process Personal Information. The Client may reasonably object on data-protection grounds; if unresolved, the Client may terminate the affected engagement for convenience without penalty. yourco remains responsible for its sub-processors and binds each to terms no less protective than this DPA. [[Counsel: confirm the list + the named payment processor.]]

## 7. Security measures
yourco maintains reasonable and appropriate technical + organizational measures, including: **encryption** in transit (TLS 1.2+) and at rest (AES-256 or equivalent) where supported; **least-privilege** access with MFA on administrative accounts and prompt revocation; **secrets isolated from source control**; an **approval gate** on any external/destructive action; access-log review + anomaly monitoring; reliance on sub-processors with recognized attestations (e.g. SOC 2) where available; confidentiality + training for personnel; and a documented **incident response approach** (the Security Incident Runbook — `agents/rafi/security-incident-runbook.md`), reviewed periodically. [[Counsel: formalize the Annex of measures.]]

## 8. Retention & deletion
During the term, yourco retains Personal Information only as needed to provide the Services and as directed. On the Client's written request, yourco **deletes or returns** Personal Information within **30 days**; and within **30 days of termination**, returns (in a usable format) or securely deletes it at the Client's election — except where law requires retention (which stays subject to this DPA). Aggregated, de-identified data may be retained.

## 9. Data-subject rights
yourco provides reasonable assistance for the Client to respond to Data-Subject requests (access, correct, delete, restrict, port). If yourco receives a request directly, it promptly forwards it to the Client and does not respond except to acknowledge or as instructed/required.

## 10. Security incidents
yourco notifies the Client of any Security Incident affecting the Client's Personal Information **without undue delay, and within 72 hours** of becoming aware — including (as known) the nature, categories/approximate numbers affected, likely consequences, and measures taken. yourco cooperates with the Client's investigation, remediation, and regulatory notifications. Neither party publicly attributes an incident to the other without prior written consent (not unreasonably withheld), except as required by law.

## 11. Audit & attestation
On the Client's written request (≤ once/year unless an incident or regulator justifies more), yourco provides: a written summary of its security program; copies of any third-party audit reports/certifications it has the right to share; and reasonable responses to a security questionnaire. In-person audits only if required by a regulator or a good-faith concern not otherwise addressable, on reasonable notice, during business hours, subject to confidentiality.

## 12. Cross-border transfers
Personal Information is primarily processed in the **United States**. If any is transferred outside the US, yourco ensures a lawful transfer mechanism (e.g. standard contractual clauses) where required.

## 13. State-specific provisions
**California (CCPA/CPRA):** yourco certifies it will not sell or share Personal Information; will not retain/use/disclose it for any purpose other than performing the Services; will not retain/use/disclose it outside the direct business relationship; and will not combine it with other sources except as permitted. **Other states (VCDPA, CPA, etc.):** yourco provides substantially equivalent assistance and compliance, adapted to each law.

## 14. General
This DPA controls over the Engagement Agreement on the processing of Personal Information. yourco may amend it without consent only as reasonably necessary to comply with changes in Privacy Laws (30 days' notice); other amendments need mutual written consent; sub-processor changes are governed by §6. Claims under this DPA are subject to the limitation of liability in the Engagement Agreement. Governed by Florida law.

---
**[[CLIENT]]** — By: ______ Name: ______ Date: ____  ·  **YourCo LLC** — By: the Founder, Authorized Member  Date: ____
> Execute alongside the Engagement Agreement (DocuSign). **Counsel review required before first use.**
