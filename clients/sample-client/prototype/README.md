# Sample Client agent — dry-run prototype

> **Dry run. Client Owner hasn't agreed to anything.** This builds the core of the Installation Proposal Automation agent and runs it on **sample, fictional data** so the Founder can see what delivering this engagement looks like. It touches **no** real Aspire account, Twilio, mailbox, customer, or database, and **sends nothing** — every "send" is a draft printed to the screen, exactly as the real agent holds drafts until a human approves.

## What's here
- `sample_proposal.txt` — a fictional signed Aspire "Installation" proposal (the Chen patio job, $48,500).
- `agent.py` — the engine: parse (Claude) → tier deposit (tested code) → draft client/supplier/sub messages (Claude) → approval gate → all-clear logic. Run: `python3 clients/sample-client/prototype/agent.py`.
- `test_agent.py` — the test suite (10 checks). Run: `python3 clients/sample-client/prototype/test_agent.py`.
- `sample-run-output.txt` — a captured live run (Claude drafting the real messages), so you can read the output without running it.
## Client-facing mockups (for showing Client Owner — sample data, nothing live)
Serve with launch config `yourco-sample-client`; start at `/index.html`.
- `index.html` — the **walkthrough hub**: the whole setup end to end, linking the screens below in order.
- `approval.html` — **Charlene's one-tap approval** of the client deposit. Email + SMS with the amount **locked** (computed, not editable). Approve / Edit / Decline; Approve flips to "on its way" with a timestamped audit line.
- `client-owner-approvals.html` — **Client Owner's approvals**: the supplier orders (shop vs job-site routing) + the sub notice, tap through them; counter decrements to "all clear."
- `status-board.html` — the **"operated" job board**: every signed job with its deposit / suppliers / subs gates, a daily nudge list, and the week's metrics. The watch-everything view.
- `greenlit.html` — the **all-clear** Client Owner + Charlene get when deposit + suppliers + subs all confirm.
- `monthly-report.html` — the **monthly outcome report**: volume, deposits, hours saved, and the reliability behind it.

All on sample data; nothing sends. They show what the engagement looks like operated, without Client Owner having signed.

## What it proves (the proposal's promises, made real)
- **Money is math, not AI.** The deposit ($16,975 = 35% of $48,500) is computed by `deposit_for()` in tested code and injected into the draft as a fixed figure. Claude is told never to change a number. The test suite checks the tiers and the boundaries.
- **Nothing sends without a human tap.** Every output is a *draft* marked "⏳ awaiting Charlene/Client Owner approval." The prototype literally cannot send — there's no Twilio, no mailbox wired in.
- **Duplicate-proof.** One signed proposal can never double-send (the `_SEEN` guard; tested).
- **Installation-only.** Maintenance/mowing proposals are filtered out (tested).
- **Ships with a test suite.** `test_agent.py` — 10/10 passing on the money math, routing, filter, duplicate guard, and missing-data handling.

## What's real vs stubbed (so the dry run is honest)
| Piece | In this prototype | In production |
|---|---|---|
| Trigger | reads `sample_proposal.txt` | Aspire webhook on `status = Signed` |
| Parse | Claude extracts the fields | same (Claude reads the Aspire payload) |
| Deposit math | tested code (`deposit_for`) | same |
| Drafting | Claude (real, live) | same, on the @sampleclient.example.com mailbox |
| "Send" | printed draft, gated | Twilio SMS + email after a human tap |
| Dates | from the sample file | Google Calendar |
| Runtime / tracing / memory | not needed to show the logic | n8n on a private server + Langfuse + a private DB |

## Placeholders to replace with Client Owner's real rules (from the system spec)
- **Deposit tiers** (`DEPOSIT_TIERS` in `agent.py`) are SAMPLE: ≤$10K → 50%, mid → 35%, ≥$150K → 25%. Client Owner's actual tier percentages come from his system spec.
- **Material routing** (`route_material`) is a SAMPLE heuristic (pallets/tons → job site, boxed → shop). Real routing rules per supplier come from Client Owner.

## The honest read
The risky, must-be-right parts — the money math, the gates, the dup-proofing, the filter — are real and tested today. The drafting brain is real and live. What's left for a real engagement is the integration wiring (Aspire, Twilio, the mailbox, the private server) and loading Client Owner's actual tier rules + templates — which is exactly the 3-week build in `../03_setup-plan-and-tech.md`.
