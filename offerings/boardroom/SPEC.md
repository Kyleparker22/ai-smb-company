# The Boardroom — Build Spec

**Working name:** The Boardroom (frontier #9)
**Author:** the Founder
**Stack:** monthly headless loop (runtime pattern) · Claude API (multi-lens deliberation) · client data pulls read-only (QuickBooks/CRM/job data — whatever the OS already integrates) · minutes rendered to the client console + PDF, R1 draft-for-approval
**Status:** Spec — see `offerings/_frontier-roadmap.md` row #9. Build trigger: **first signed client, month 2.**
**Pillar / form factor:** Company Brain (pillar 7) with Back Office (6) data feeds; form factor 2 (headless monthly loop) delivering through form factor 3 (console + minutes doc).

---

## 1. Concept

A board of directors for businesses too small to have one. Once a month, the client's OS convenes a **board meeting on the client's real numbers** — the actual month's revenue, AR aging, pipeline, job margins, whatever the engagement already integrates — deliberated through **distinct generic expert lenses**: a CFO lens (cash, margin, concentration risk), a skeptical-customer lens (why would I churn? what's degrading?), an operator lens (bottlenecks, capacity, key-person exposure — feeds the Understudy conversation). Additional lenses scoped per client (a sales lens, a compliance lens for regulated trades). **One seat carries mandated dissent**: every meeting, it must file a written objection to the month's prevailing conclusion or to a decision the owner has signaled — structurally, not when it happens to feel contrarian. Output is **real minutes**: agenda, what the numbers said, each lens's position, the dissent, open questions for the owner, and a resolutions table tracked meeting-over-meeting (last month's resolutions get a status line — the board remembers).

The owner of a 12-person business has no one whose job is to disagree with them on the numbers. Their accountant is backward-looking, their spouse is tired of hearing about it, their employees won't say it. The Boardroom is the missing governance ritual, at SMB price, with the one property human advisory boards famously lack: dissent that cannot be socially suppressed, because it's mandated by rubric.

**Hard rule, load-bearing, restated in §8:** lenses are **generic roles only** — "a CFO lens," never "Warren Buffett." Simulating named real people on a client-facing surface would violate yourco's no-fabricated-endorsement rule (the internal advisory-panel skill exists for yourco's own decisions and is explicitly barred from external use; this product is that rule's public-facing mirror, built clean from the start).

## 2. Why it's never been done

Human versions exist and exclude the market: real boards are for funded companies; peer groups (Vistage, EO) cost $10–20k/yr, meet on self-reported anecdotes not live data, and dissent is socially optional. AI versions to date are chat toys — "ask a CEO persona" — grounded in nothing, remembering nothing, accountable to nothing. The unlock is an *operated* board: standing read integration into the client's real systems (so the meeting runs on actual numbers, not what the owner remembers to paste in), month-over-month memory (resolutions tracked, dissents scored in hindsight), and an eval layer on the board itself (was the CFO lens's arithmetic right? did dissents prove material?). That triple — live data, persistent governance memory, evaluated quality — needs the moat layer under it, which is why chat-tool copies stay toys.

## 3. Build shape

| Piece | What it is | Notes |
|---|---|---|
| Board charter (per client) | Which lenses sit, data sources in scope, topics out of scope (client sets), meeting day, owner's standing questions | 1-page template, set at onboarding |
| Data brief compiler | Pre-meeting loop: pull the month's read-only extracts → normalized brief (P&L movement, AR, pipeline, ops metrics) with **source stamps on every figure** | Reuses the engagement's existing integrations; no new write access ever |
| The deliberation | Structured multi-lens pass over the brief: each lens produces position + evidence refs; the dissent seat produces its objection **against the drafted consensus** (it reads the others' positions first — dissent must engage, not free-associate) | One orchestrated Claude run, lens prompts kept in the template, per-client overlay only for scoped lenses |
| Minutes renderer | House minutes format: agenda · numbers summary · positions by lens · **the dissent, verbatim** · questions for the owner · resolutions table w/ prior-month status | R1 draft → the Founder/approver review → delivered to console + PDF |
| Hindsight scorer | Quarterly Kolby pass: arithmetic spot-check vs. sources; dissent audit — which objections proved material? which misses did no lens flag? → learnings feed the lens prompts | The board is itself eval-gated; this is what keeps it from decaying into horoscope |

**Data sources:** whatever the engagement already integrates, read-only (QuickBooks/accounting extract, CRM/pipeline, ops/job data); a client can run a thin Boardroom on accounting data alone. **Effort band:** M — lens prompts + minutes format + deliberation orchestration ~3–4 days generic in the template; per-client onboarding S (~half day: charter + brief wiring).

## 4. Moat fit

Executive trust is the product itself — this is the moat's "trust" leg sold directly. It deepens integration (the board is a reason to connect the accounting system even when no module automates it yet — integration depth ahead of automation, pure moat). It is evaluated advice: the hindsight scorer makes "was the board right?" a measured question, which no advisory product on earth currently answers — and the eval record feeds the Trust Ledger (#1) and the Self-Proving Invoice (#4: "board: 12 resolutions tracked, 3 dissents, 1 proved material"). Expansion engine: every meeting's minutes surface the next module ("AR aging flagged three months running" → the invoice-chaser module; "key-person exposure" → Understudy #7). The board is a standing, client-funded discovery loop. And the dissent seat differentiates against every sycophantic AI-advisor product the commodity layer will ship: mandated, evaluated dissent is a governance mechanism, not a prompt.

## 5. Gates / compliance

- **Not a fiduciary board, and never presented as one.** No legal governance role, no fiduciary duty, no voting authority. The charter and every minutes doc footer state: analysis and questions for the owner's judgment; all decisions remain the owner's.
- **Advice boundaries (autonomy matrix "regulated advice" row):** the board frames observations and questions; it does not render investment advice, tax positions, or legal conclusions. Where a topic crosses that line the minutes say "question for your CPA/attorney" — modeled on the Care/Conduit draft-never-determine rule. Prohibition on personalized investment/financial advice is absolute.
- **Counsel gate:** minutes-format disclaimer language rides the legal-suite review (gate #1, `processes/counsel-gates.md`). No new standalone gate.
- **Approval:** minutes are client-facing → R1 draft-for-approval, standard climb rules apply only to delivery mechanics, never to skipping review of substance in early months.
- **White-label:** the board is "the [Client] board" on all client-facing surfaces. Financial data handled per house PII/confidentiality posture; board briefs never leave the client's tenant scope.

## 6. Pricing frame *(assumption-stated; Polo locks)*

A Company Brain module on the standard band: **~$1–2k setup** (charter, lens scoping, data wiring) **+ ~$500–1,500/mo** standalone — deliberately under the human-peer-group anchor (~$10–20k/yr) while being data-grounded, which they aren't. Expected dominant mode: **bundled into Suite-and-up OS levels** as the governance layer, where its real value is the expansion surface (§4) — there it prices as part of the OS band, not a line item. Month-2 add-on offer to every signed client. Illustrative until evidence.

## 7. Activation trigger (build)

**First signed client, month 2** (roadmap sequencing #2). Month 1 belongs to the first module's go-live; the board convenes once there's a month of real data and earned standing. Generic lens prompts + minutes template may be drafted into `_yourco-template` at any time (doc work, no client dependency).

## 8. What we will NOT do

- **No simulated real people. Ever. Hard rule.** No named individuals, living or dead — no "Buffett seat," no "what would Elon say," no thinly-renamed soundalikes, regardless of client request (and clients *will* request it). Generic professional lenses only. This is yourco's no-fabricated-endorsement rule applied to product; one violation contaminates the company's credibility gate everywhere.
- **No decisions.** The board advises and questions; it holds zero autonomy over any client action. Nothing the board says triggers an agent action without the standard approval path.
- **No investment, tax, or legal determinations** — flagged to licensed humans, always.
- **No fabricated numbers or precision theater.** Every figure in the brief carries a source stamp; missing data renders as "not integrated yet" (itself a useful expansion signal), never estimated silently. No confidence percentages dressed as rigor.
- **No sycophancy by design *or* dissent theater.** The dissent seat is evaluated on hindsight materiality — it must object where objection is warranted, not perform contrarianism to fill the mandate; a dissent seat whose objections are noise fails its eval the same as one that flatters.
- **No minutes without memory.** A Boardroom deployment that doesn't track its resolutions table month-over-month is not shipped — the memory is the product; a stateless board is the chat toy we're distinct from.
