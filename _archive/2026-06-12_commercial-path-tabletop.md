# Commercial-path tabletop dry-run — 2026-06-12

> Walk the **money path** end-to-end on paper — proposal → sign → deposit → onboard → build → go-live → console → readout → offboard — and find the seams *before a real deal hits them.* The delivery dry-run (Northside dental) proved the *build*; this tests everything we shipped this session as one connected flow. Subject: **"Greenline Landscaping"** (sample), flagship intake employee **"Reese,"** landscaping pricing locked (~$4k build + $750/mo — *as of 2026-06-12; since superseded by the $1,500/mo on-ramp floor + OS tiers, `pricing/v0/os-tiers.md`*). Red-team tone: the happy path is assumed; only the breaks are logged.

## The walk (stage → what happens → where it BREAKS)

**1 · Lead → Proposal.** Reilly/Sadie source → David qualifies → discovery (Janice/the Founder) → Pickle+Polo fill `proposal-sow.md` from discovery + locked pricing → send for signature.
- 🔴 **BREAK — the proposal is Markdown; it isn't sendable/signable.** There's no branded, rendered (PDF/HTML) proposal to drop into DocuSign. The one-pager and pitch deck are HTML; the proposal is a `.md` template. *Someone/something must render MD → branded doc.* Owner: Pickle/Webb.

**2 · Sign.** Client e-signs; the Founder counter-signs.
- 🔴 **BREAK — the signing packet is undefined and unsendable.** What goes in the DocuSign envelope? The SOW *attaches to* the Engagement Agreement + DPA (+ BAA if regulated) — but the assembly/order isn't specified, and **every one of those contracts is stamped "counsel must review before use."** So today this step *cannot execute at all.* Reconfirms: **counsel review is the true gate.** Owner: Ray/Rafi/the Founder + counsel.
- 🟠 **SEAM — which contract bundle per vertical?** Rafi's vertical-compliance-map should pick "needs BAA / extra clauses," but it isn't wired into the signing step. Owner: Rafi.

**3 · Deposit (Stripe).** Charles sends the build-fee link on signing; client pays.
- 🔴 **BREAK — Stripe isn't set up** (the Founder's pending action). Step can't run today. Known.
- 🟠 **BREAK (the best catch) — ACH clearing time collides with the 48h promise.** We chose **ACH-preferred** (to protect margin). ACH takes **1–4 business days to clear.** If go-live is gated on the deposit *clearing*, and we promise **48h**, the payment rail can blow the promise by itself. The two things we shipped this session contradict each other. *Resolution needed:* define the clock-start as **signed + access granted + deposit authorized** (not cleared), or take the deposit by **card** (instant) when speed matters. Owner: Charles/Polo. → fixed below.

**4 · Onboard.** Janice: provision `reese@greenline-domain`, get tenant access (the Founder-approve), pre-call intake.
- 🟠 **BREAK — the 48h clock depends on client-side work we don't control.** Granting Workspace/calendar/CRM access, email DNS, forwarding/porting the phone number — all client tasks. A slow client blows 48h through no fault of ours. There's **no "client-readiness pre-requisite" gate that starts the clock.** The clock-start rule existed only in the *declined* 48h-guarantee doc — so it's orphaned while "48h from signing" is still promised live. Owner: Janice. → fixed below.
- 🟡 Employee-identity provisioning (Workspace tenant, `employee@client-domain`) is documented but **never tested end-to-end.** Owner: Janice/Kemba.

**5 · Build → Eval → Go-live (the 48h).** Kimi builds on `yourco-template` → Kolby evals (rubric + adversarial + gates) → go-live (the Founder approves, Phase 0/1).
- ✅ Proven in the prior delivery dry-run. Eval gate before go-live holds.
- 🟠 **BREAK — the console is sold in the proposal ("your live console") but its live data feed is unbuilt.** The console is a static template with sample data; wiring it to the client's real activity/approvals is the same unbuilt plumbing class as Instant Employee Mode B. At a real go-live it can't show real data yet. *Either build the feed, or scope console v1 honestly* (e.g., daily-refreshed digest, not real-time). Owner: Webb. → launch-runbook.

**6 · Use daily / See value.** Console + weekly readout.
- 🟡 **Weekly readout still untemplated** (gap-audit backlog). The console mitigates but the proactive executive-trust email isn't built. Owner: Kortney.

**7 · Expand.** Bird scopes employee #2 → new SOW (build fee + retainer step-up).
- ✅ The proposal/SOW supports this cleanly. Same machine. No break.

**8 · Offboard.** `offboarding.md`: pause/exit, data export, DPA deletion.
- 🟡 **SEAM — data-export mechanism unspecified.** "Package CSV/JSON/PDF and deliver securely" — but *from where, how?* For landscaping intake much data already lives in the client's own CRM (good), but YourCo-side logs need an actual export path. Owner: Janice/Kemba.
- 🟡 **VERIFY — does the DPA state a concrete deletion SLA?** Offboarding points to "the DPA-specified window"; confirm the DPA actually defines one (and counsel blesses it). Owner: Rafi.

## Findings — prioritized

| # | Sev | Finding | Owner | Action |
|---|---|---|---|---|
| 1 | 🔴 | Contracts counsel-pending → signing can't execute (the real gate) | the Founder + counsel | Engage counsel during the OtherVenture wait |
| 2 | 🔴 | Stripe not set up | the Founder | Account + bank setup (`payments.md` checklist) |
| 3 | 🔴 | Proposal is un-rendered Markdown (not signable) | Pickle/Webb | Build a branded proposal render (HTML→PDF) |
| 4 | 🟠 | **48h clock undefined in live artifacts; collides with ACH clearing + client-access delay** | Charles/Janice | **Define clock-start = signed + access granted + deposit authorized** — fixed now |
| 5 | 🟠 | Console sold but live data feed unbuilt | Webb | Build feed OR scope v1 honestly → launch-runbook |
| 6 | 🟠 | Signing packet + per-vertical contract bundle undefined | Ray/Rafi | Define the DocuSign envelope; wire compliance-map |
| 7 | 🟡 | Weekly readout untemplated | Kortney | Template it |
| 8 | 🟡 | Data-export mechanism + DPA deletion SLA unverified | Janice/Rafi | Specify export; confirm DPA window |
| 9 | 🟡 | Employee-identity provisioning untested e2e | Janice/Kemba | One real test provision |

## The pattern (feed-forward)
The breaks cluster in the **same place the gap audit found** — the commercial edges (sign, pay) and the promise-vs-reality seams (console, 48h). Reinforces the learning: the OS was built product-first; the deal mechanics and the honesty of the live promises need the same rigor. **Two live promises now have surfaced dependencies — "48h" (payment + access) and "your live console" (data feed) — and a promise you can't yet keep is worse than one you don't make.**

## Fixed in this run
- **#4** — clock-start defined + wired into the proposal + onboarding + payments (below). The rest are logged with owners; #3 and #5 are the next builds.
