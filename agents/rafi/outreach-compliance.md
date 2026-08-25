# Outreach Compliance — CAN-SPAM checklist + FTSA/TCPA gate

> **Owner: Rafi.** The go-live gate Reilly's outreach must clear before any send. Email requirements (CAN-SPAM) are well-defined and checklist-able below. SMS (TCPA/FTSA) is higher-risk and **needs counsel sign-off** — this is a prep brief, not legal advice.

## Recommendation: email-first
Email outreach is straightforward to make compliant (below). SMS marketing without prior consent carries real legal risk (TCPA + Florida's FTSA, which has a private right of action). **Recommend launching email-only**, and deferring SMS until 10DLC is approved, a consent mechanism exists, and counsel signs off. This also matches the email-only decision the sales loop has surfaced.

## CAN-SPAM checklist (email — verify before first send)
Every Reilly campaign in `agents/reilly/copy-structure.md` must satisfy all of these:
1. **Accurate header info** — From / Reply-To / routing identify yourco truthfully (real sending domain, real name). ☐
2. **No deceptive subject lines** — the subject reflects the message. ☐
3. **Identifies as outreach** — the message makes clear it's a business solicitation (the honest, problem-first tone already does this). ☐
4. **Valid physical postal address** — YourCo LLC's real mailing address in every email footer. ☐ *(add to the Instantly template footer)*
5. **Clear opt-out** — a working unsubscribe/opt-out in every email. ☐
6. **Honor opt-outs within 10 business days** — and keep honoring for ≥30 days. ☐ *(Reilly's `_suppression.md` must auto-honor replies/unsubscribes/DNC)*
7. **Responsible for vendors** — yourco stays liable even though Instantly sends. Confirm Instantly is configured to all of the above. ☐

→ Rafi verifies this list (with Reilly) before the first batch; the Founder gives the final send approval.

## SMS — TCPA / FTSA (counsel gate; do not send until cleared)
High-level, **not legal advice** — for counsel to confirm:
- **TCPA (federal):** marketing texts generally require prior express written consent; autodialed/automated sends without it are a violation.
- **FTSA (Florida):** stricter — covers automated/prerecorded/text "telephonic sales calls," requires prior express written consent, and has a **private right of action** (litigation exposure). Amended in 2023 but still material.
- **What's needed before any SMS:** (a) 10DLC registration approved (`processes/10dlc-sending-infra-setup.md`, in progress); (b) a documented consent mechanism; (c) **counsel sign-off** on the approach; (d) the Founder's go.

## Sign-off tracker
| Gate | Status | Owner |
|---|---|---|
| CAN-SPAM checklist (email) | 🟡 verify before send (footer address + unsubscribe in template) | Rafi + Reilly |
| 10DLC registration | ⏳ in progress | the Founder |
| FTSA/TCPA counsel sign-off (SMS) | 🔴 required before any SMS | counsel + the Founder |
| Suppression auto-honored | 🟡 confirm in Instantly | Reilly |

> **Go-live rule:** no email sends until the CAN-SPAM checklist is fully ☑; **no SMS at all** until the FTSA/TCPA gate clears. Email-first is the recommended launch.
