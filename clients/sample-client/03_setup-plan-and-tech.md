# Sample Client — setup plan & technology

> The build plan the Founder sent. Original: `attachments/YourCo — Setup Plan & Tech (Sample Client).pdf`.

## What happens when a proposal signs (plain English)
1. Aspire tells the employee the moment an **Installation** proposal hits Signed; anything else is ignored.
2. It reads the proposal, checks the job calendar, applies the payment tiers, sorts materials (shop vs job site), spots any sub work.
3. It drafts everything: client deposit email + text, one order email per supplier, one notice per sub.
4. **Charlene approves client messages; Client Owner approves supplier and sub messages** — one tap. Until then, nothing leaves the building.
5. When deposit, suppliers, and subs are all confirmed, both get the "greenlit — all systems go" email. Anything stuck too long is flagged daily.

## The technology — and who owns what
| Piece | What it does | Owned by |
|---|---|---|
| **Aspire** | System of record, unchanged. Notifies the employee on signed proposals; supplies job details. | Sample Client |
| **Email & calendar** | A real `@sampleclient.example.com` mailbox — the employee's identity. Sends/receives as itself; reads the job calendar. | Sample Client |
| **Texting line** | A Twilio number registered to Sample Client — texts come from the company, not a third party. | Sample Client |
| **The brain** | Claude (Anthropic) — drafts emails + texts. Words only; every dollar is computed by tested code, never AI. | yourco |
| **The workbench** | n8n on a private server dedicated to Sample Client — executes every step, keeps the full run history. No shared cloud automation accounts. | yourco |
| **The memory** | A private database tracking every job: drafts, approvals, deposit status, supplier + sub confirmations. | yourco |
| **Quality control** | Langfuse — every action traced; a test suite of real proposal scenarios re-runs before any change ships. | yourco |
| **Watchdogs** | Uptime monitors + auto-restart. A 2am hiccup is known within minutes. | yourco |

Rule: anything carrying Sample Client's identity (email, phone, Aspire, data) is theirs; the machinery that runs it is yourco's to own, maintain, and pay for.

## Build plan — three weeks
- **Week 1 — wire it up:** private server stood up; Aspire, email, calendar, texting connected; payment-tier rules loaded as tested code.
- **Weeks 1–2 — build & prove:** the three workflows built, then run against real past proposals + a 10-scenario checklist (no subs, under $10K, over $150K, duplicates, missing calendar dates…). All must pass.
- **Week 3 — shadow mode, then live:** runs every real signed proposal, only the Founder sees output; drafts compared to what Charlene actually sends, gaps tightened, then approvals switch on and it's live.

## Safeguards (the moat, in one breath)
Nothing reaches a customer, supplier, or sub without a human tap. Approval links are secure and one-time — can't be triggered by spam filters or forwarded emails. Money is math, not AI. One signed proposal can never double-send. Every send is logged: what, to whom, approved by whom, when.

## Stack note for delivery (Kemba / Kimi)
This engagement uses **n8n on a private per-client server + Claude + Langfuse + Twilio + Google Workspace + Aspire webhook** — a text/automation build, not a voice agent (so not the Vapi stack). n8n-as-glue here is the bounded "wrench, not the workshop" exception under yourco's eval/approval umbrella (per `decisions/2026-06-11_no-code-tooling-stance.md`): yourco owns and instruments it; the brain logic and the gates are yourco's, the dollar math is tested code.
