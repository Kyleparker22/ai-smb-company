# Vertical → Compliance-Gate Map

> **Owner: Rafi.** Read at **discovery** so the vertical's compliance gate is surfaced on the call — not discovered at go-live. Each vertical can carry a gate that *blocks go-live until cleared*. Flags only; counsel + the Founder clear the gate. (Surfaced by the Northside dental dry-run, which hit the HIPAA-BAA gate.)

| Vertical / data | Gate | What it triggers | Owner |
|---|---|---|---|
| **Healthcare** (dental, medical, therapy, vet, etc.) — PHI | **HIPAA BAA** required before any PHI flows | Sign `processes/contracts/baa.md`; minimize PHI; no clinical advice by the employee | Rafi + Ray |
| **Financial services / lending** — consumer financial data | **GLBA** Safeguards + privacy (and FCRA if credit data) | Confirm scope; safeguards posture; likely a tailored DPA addendum | Rafi + counsel |
| **Legal** — client confidences | **Attorney-client privilege** + confidentiality | Privilege-preserving handling; tightened access; no training on content | Rafi + Ray |
| **Children's services / education** — minors' data | **COPPA / FERPA** | Consent posture; data-minimization; confirm before any minor data | Rafi + counsel |
| **Outbound for any vertical** — email/SMS | **CAN-SPAM / TCPA / FTSA** | Already covered: `agents/rafi/outreach-compliance.md` + 10DLC | Rafi |
| **General B2B / home services** — business-contact data | Standard DPA (no special gate) | `processes/contracts/dpa.md` | Rafi |

## How discovery uses this
At the discovery call, Kimi/Janice ask the vertical + whether the employee touches regulated data. If a gate applies → it's a **hard go-live gate** in `03_eval` (gate #8), surfaced immediately so counsel/the agreement can be lined up inside the 48h, not after.

> Living map — add a row whenever a new vertical's gate surfaces (e.g. from a dry-run or a real engagement).
