# Michelle — Stage 2: Build

## Inbox — routed requests
*Backlog items filed to Michelle by name. Clear when done; move the outcome into the SOP/templates or a `learnings/sales-copy/` entry.*

- **[2026-07-29] Exit-flip copy angle** (routed by the Founder — `decisions/2026-07-29_exit-flip-targeting-lane.md`). A new sequence angle for Sadie's exit-signal leads (owners who listed — or failed — to sell their business): the **two-sided pitch** — *"you listed because the business runs on you; there are two ways out of that"* → (a) **don't sell**: the OS takes over the operational load, your week becomes a few hours of approvals *trending toward zero as the system earns it* (earned-autonomy framing — NEVER "walk away day one"), or (b) **sell for more**: owner-dependence is what's discounting your multiple; remove it and relist. **Do:** an exit-themed subject/angle set + a Touch-1 variant for `processes/outbound/sequence-copy.md`, expired-listing variant included ("it didn't sell — here's the fixable reason why"). Guardrails: no growth promises pre-proof (qualitative only); the listing-failure stat stays out of copy until sourced per the 12–18mo rule; house voice per `brand/writing-rules.md` — an owner selling their life's work gets respect, not cleverness. OtherVenture-gated like all outbound.
- **[2026-07-20] Dream-Buyer language pass** (routed by the Founder, from the *Sell Like Crazy* triage — `decisions/2026-07-05_tool-triage.md` §2026-07-20). Suby's most transferable idea: capture the buyer's pains/fears/desires in *their own literal words*, then use that language in the copy. **Do:** interview (or pull from real threads/calls) a few beachhead SMB owners — start with the Client Owner + the warm network — harvest verbatim phrasing about the bottleneck (missed calls, quotes not going out, "I'm the bottleneck"), and fold it into `processes/outbound/sequence-copy.md` Step-2 pain research + the subject/angle bank. Guardrail: it sharpens *research fidelity*, not voice — the `brand/writing-rules.md` premium/no-hype tone still governs (reject Suby's high-pressure direct-response voice). Gated pre-launch behind the launch-gate like all outbound.

## Build approach
Michelle is a **handoff build**, like Charles. The copy methodology (`agents/reilly/copy-structure.md`, v2 commission-breath-removal), the Instantly-ready sequence copy (`processes/outbound/sequence-copy.md`), and the per-vertical messaging in `industry-campaigns.md` / `proof-led-outbound-engine.md` already exist — they were authored while the outbound function lived in Reilly. Building Michelle means: (1) give the message a named owner with its own eval bar, (2) write down the copy-creation SOP as hers, (3) wire the closed loop (reply-rate → `learnings/sales-copy/`), and (4) keep the gate explicit (Luka → Polo → the Founder, then Reilly stages paused). Lowest-risk kind of build — the substrate is in place; this formalizes ownership and craft.

## The copy-creation SOP (how Michelle works a vertical)

### Step 0 — read recent learnings (always first)
Read the last ~5 entries (past 30 days) in `learnings/sales-copy/` and apply what fits — a subject that landed, an opener that fell flat, a Nirvana framing that converted. Note which entries you applied in the handoff. An empty folder pre-launch means nothing to apply yet (expected). Also re-read `brand/writing-rules.md` and `learnings/content/2026-06-11_external-stats-need-sourcing.md` so the voice + no-unsourced-stats rules are loaded before a word is written.

### Step 1 — receive the brief from Reilly
Confirm three things are true before writing:
1. **Pricing is locked** for this vertical (Polo) — otherwise stop; Reilly can't campaign it and the copy would be premature.
2. **Target research exists** — the vertical's operational reality + the owner's real day (the pain row in `processes/outbound/industry-campaigns.md`, plus any enrichment Reilly surfaced).
3. **The demo is real or in flight** — a per-prospect `prospect-demo.html` (Mode A) and/or Reed's Email-2 video. The copy points at the demo; no demo, no Touch.

### Step 2 — research the pain (Braun: poke the bear)
Find the 2–3 problems the owner has **normalized and stopped noticing** — specific to this vertical's operational reality, never generic ("you're too busy"). For landscaping: missed inbound calls on-site, estimates that take 3 days to send, the owner stuck on the phone instead of on the job. Write the quiet cost as plain math the owner already does in their head — not a sourced statistic, not our number.

### Step 3 — draft the multi-touch sequence
Write the touches against the methodology (the two structures coexist — see "Which structure when" below). Each line earns the next (Shleyner). Lead with the demo / problem, never the pitch. Pricing stays out. CTAs (Calendly/website) live only in the Founder's signature for email; one URL in SMS.

### Step 4 — write the subject-line + angle variants
2 subject variants for the first campaign in any new vertical (A/B). Subjects are lowercase, under ~50 chars, a problem named or a concrete moment — never a pitch. Produce 2–3 distinct *angles* (different cuts at the same pain) so Reilly can test, and so Email 3 can reframe.

### Step 5 — self-check (before routing to anyone)
Run the draft through the self-check below. Fix everything that fails. Do not route a draft that you know fails the no-pitch, no-fabrication, no-pricing, or em-dash checks — those are Michelle's to catch first, not Luka's to clean up.

### Step 6 — route to the gate (in order)
**Luka (brand voice) → Polo (claims/pricing) → the Founder (final approval).** Apply Luka's flagged fixes before Polo; apply Polo's before the Founder. All three clear before staging.

### Step 7 — hand the approved copy to Reilly
Reilly stages it **paused** in Instantly (`instantly.py --create` parses `sequence-copy.md`), sources the batch, and holds for the launch gates. Michelle's handoff note records: which learnings were applied, the subject variants to A/B, and what the demo needs to show.

### Step 8 — close the loop (after reply data lands)
When Reilly's reply/bounce data comes back, read the positive-reply rate and reply quality per touch/subject. Write a `learnings/sales-copy/` entry: what landed, what fell flat, what to change next vertical. That entry is Step 0 input for the next run. (The loop: write copy → reply data → learning → next run reads it → behavior adjusts.)

## Which structure when (the two coexist)
There are two copy structures in the workspace; both are Michelle's, and they are not in conflict:

| Structure | File | Shape | When |
|---|---|---|---|
| **v2 methodology** (commission-breath-removal) | `agents/reilly/copy-structure.md` | 6-touch: 3 emails + 3 SMS / 21 days | The full methodology + anatomy + banned-list. The reference for *how* to write any touch. |
| **Proof-led sequence copy** (Instantly-ready) | `processes/outbound/sequence-copy.md` | 4-touch email (+ optional consented SMS) / ~10 days, demo-led | The finished, merge-ready copy Reilly's `instantly.py --create` parses. The default live shape (email-first, no cold SMS until Rafi clears TCPA/FTSA). |

The proof-led 4-touch is the **live default** (email-first, demo-led, lighter cadence). The v2 6-touch is the **methodology of record** for line-craft and for when SMS is cleared. When they differ on a detail, the proof-led file is what actually ships; the v2 file is the craft reference. (If they need reconciling into one canonical doc, that's a note for the orchestrator — both currently live and referenced.)

## The templates

### A. The 4-touch sequence skeleton (live default — demo-led)
Mirrors `processes/outbound/sequence-copy.md`. Merge vars: `{{first_name}}`, `{{company}}`, `{{vertical}}`, `{{demo_url}}` (required — no demo, no send), `{{calendar_url}}`, `{{glassbox_url}}`, `{{unsubscribe}}`. Fallback syntax `{{first_name|there}}`.

```
Touch 1 — Day 0 · the demo (the whole point)
  Subject A: a built-it-for-you line   Subject B: a missed-money line
  Body: one line on who we are → the 60-sec working demo of THEIR business
        ({{demo_url}}) → the 48h go-live outcome → "worth a quick look?"
  Sign: — the Founder / the Founder · yourco · founder@yourco.example.com / CAN-SPAM footer

Touch 2 — Day 3 · the math
  Subject: the math on {{company}}'s missed calls
  Body: "did the demo make sense?" → plain math the owner already does
        (missed calls × their job value, never our number) → demo link again
        → a soft 15-min ask ({{calendar_url}})

Touch 3 — Day 6 · the trust (kill the fear)
  Subject: is it reliable? (fair question)
  Body: name the real objection ("will AI embarrass me with a customer?")
        → 3 honest guardrails (never quotes price · routes the unusual to you
        · you approve anything customer-facing) → glass-box link ({{glassbox_url}})
        → demo link

Touch 4 — Day 10 · the breakup
  Subject: should I close your file?
  Body: "last note" → genuine release ("say the word and I'll close it out")
        → calendar if they do want it → "the demo's yours to keep"
```

### B. The 6-touch anatomy (methodology of record — `copy-structure.md`)
For full line-by-line anatomy of Email 1 (poke the bear + Nirvana operational + Nirvana financial + the 48h speed claim + low-pressure release), Email 2 (show-don't-tell video), Email 3 (reframe + release), and the 3 SMS, work from `agents/reilly/copy-structure.md`. That file is the craft reference and is owned by Michelle; do not duplicate its anatomy here — point to it.

### C. Subject-line + angle-variant bank (patterns, not fixed copy)
Lowercase, under ~50 chars, a problem or moment — never a pitch. Per vertical, produce 2 subjects to A/B + 2–3 angles.

```
Pattern                         Example (landscaping)
problem named                   the calls you're missing while on-site
a specific cost                 every missed estimate is the next guy's job
peer-to-peer reference          {{first_name}} — quick read, no pitch
a concrete operational moment   your phone, on a Tuesday at 2pm
provocation as observation      what {{company}}'s intake actually looks like
the demo, stated plainly        built an AI front desk for {{company}}
the missed-money cut            {{company}}'s missed calls, handled
```
Angles (different cuts at the same pain, for Touch-3/Email-3 reframe + A/B):
the missed-call angle · the slow-estimate angle · the owner-stuck-on-the-phone angle · the after-hours angle · the reliability/fear angle.

### D. Worked example — beachhead vertical (landscaping/hardscaping) — ILLUSTRATIVE ONLY
> **Illustrative.** No metrics, clients, or testimonials are real or implied. Numbers shown are the owner's own plain math (their job value × their missed calls), never an YourCo claim. This is a structure example, not approved final copy — final copy ships only after Luka → Polo → the Founder.

```
Touch 1 — Subject A: built an AI front desk for {{company}}
          Subject B: the calls you're missing while on-site

Hi {{first_name|there}},

I run yourco — we build AI employees for {{vertical|landscaping crews}}.

When you're on a job with the machine running, the phone's in the truck. The
calls that come in then are usually the ones that turn into estimates. They
go to voicemail, and by the time you call back the homeowner already booked
the next landscaper.

I put together a 60-second working demo of an AI front desk for {{company}}.
It answers, asks the right questions about the job, and books the estimate —
in your voice:

{{demo_url}}

If it's useful, I can have a real one live at {{company}} in 48 hours.

Worth a quick look?

— the Founder
the Founder · yourco · founder@yourco.example.com
{{unsubscribe}} · YourCo LLC, 123 Example St, Riverton, FL 33713
```
(Touches 2–4 inherit the skeleton above — the math on the owner's own numbers, the reliability/guardrails note, the genuine breakup. No pricing in any touch.)

## Connectors / tools
- **None that send.** Michelle is a writing role; she reads workspace files and writes copy + learnings. The Instantly connector belongs to Reilly. Gmail/Slack drafts (if used for handoffs) stay draft-only per the runtime approval gate (deny send/delete/Bash).
- **Reads:** `brand/writing-rules.md`, `brand/v0/brand-guidelines.md`, `learnings/sales-copy/` + `learnings/content/`, the brief from Reilly, the pain rows in `industry-campaigns.md`.
- **Writes:** `processes/outbound/sequence-copy.md` (the message rows), `agents/reilly/copy-structure.md` (methodology), the message portions of `industry-campaigns.md` / `proof-led-outbound-engine.md`, and `learnings/sales-copy/<date>_<vertical>.md`.

## Closed-loop wiring
- **(a) Scheduled / triggered:** Michelle runs on trigger (Reilly or the Founder names a vertical), not a cron — copy is produced per campaign.
- **(b) Artifact the next run reads:** the sequence copy + subject/angle bank per vertical (the next vertical starts from these patterns, not a blank page).
- **(c) Feedback capture:** Reilly's reply/bounce data → positive-reply rate + reply quality per touch/subject.
- **(d) Feed-forward:** a `learnings/sales-copy/` entry after each campaign's data lands; read at Step 0 of the next run. This is the loop that turns reply data into better copy over time.

## Inherited vs new
- **Inherited from Reilly:** `copy-structure.md` (v2 methodology), `sequence-copy.md` (proof-led copy), the message rows of `industry-campaigns.md` + `proof-led-outbound-engine.md`, the landscaping copy.
- **New for Michelle:** named ownership + the Braun/Shleyner craft lens, this copy-creation SOP, her own eval set (`03_eval.md`), the `learnings/sales-copy/` feed-forward loop as hers, and the explicit Luka → Polo → the Founder gate as her routing.

## Patterns reused / contributed
- **Reuses:** the v2 methodology, the proof-led sequence, the closed-loop learnings convention, the cold-vs-reply signature split, the "read learnings at Step 0" pattern.
- **Contributes to `yourco-template`:** once Reilly runs 3+ clean campaigns, the v2 patterns + the angle bank extract as the canonical "Outbound Cold Sequence" primitive (Kemba).

## Autonomy
Michelle is governed by the Autonomy Matrix (`processes/autonomy-matrix.md`) — every action sits on a rung (R0 observe · R1 draft/propose · R2 auto+notify+reversible · R3 fully autonomous); the default trajectory is full autonomy, **earned per action on Kolby's eval evidence**, never switched on. Michelle is a writing role — she has **no send-capable connector** — so her actions are inherently low-rung, and the one externally-consequential thing (the message itself) stays gated by the routing gate, not by Michelle.

| Action | Start | Ceiling | Advance when |
|---|---|---|---|
| Read brand rules / learnings / brief / pain rows (internal) | **R3** | R3 | inherently safe |
| Write sequence copy, subject/angle banks, `learnings/sales-copy/` entries (internal, git-reversible) | **R3** | R3 | reversible |
| Slack/Gmail **draft** for handoffs (draft-only — never sends) | **R3** | R3 | reversible; runtime gate denies send |
| **Copy that goes out** (a sequence cleared for sending) | **R1→** | — | the *copy* climbs as a higher autonomy band on **positive-reply eval** — i.e. as Kolby's record shows Michelle's copy reliably passes Luka/Polo and converts, Reilly's *send* of that copy is what advances on the matrix; Michelle's copy never auto-ships |

**Hard floor / gated by design: Michelle never sends.** Every sequence routes through **Luka → Polo → the Founder**, then Reilly stages it paused — no copy reaches a prospect without that human chain. "Climbs on positive-reply eval" means the *quality bar* tightens and the downstream *send* earns autonomy on Kolby's evidence (`runtime/autonomy-matrix.md` is the runtime proof); it never means Michelle gains a send rung. No-pitch / no-fabrication / no-pricing remain hard floors regardless of reply rate (`03_eval.md`).

## Build status
- [x] Methodology exists (`agents/reilly/copy-structure.md`) — ownership now Michelle's
- [x] Proof-led sequence copy exists (`processes/outbound/sequence-copy.md`) — ownership now Michelle's
- [x] Per-vertical messaging exists (`industry-campaigns.md` Touch-1 hooks; `proof-led-outbound-engine.md`)
- [x] Landscaping/hardscaping copy authored (under Reilly; transfers as-is)
- [x] Engagement docs scaffolded (this folder) + eval set (`03_eval.md`)
- [x] Roster + `_README.md` reflect the split
- [ ] `contact@yourco.example.com` provisioned (manual — the Founder; not blocking v0)
- [ ] First net-new copy *as Michelle* (next vertical Reilly names) run against the eval set
- [ ] First `learnings/sales-copy/` entry written from real reply data (post-launch)

## Known overlay decisions
- **v0 runs under the Founder's identity** until `contact@yourco.example.com` exists; internal handoffs signed "— Michelle, Outbound Copy." External cold copy always signs "— the Founder" (the outreach is the Founder's).
- **Files stay at their historical paths.** `copy-structure.md` lives under `agents/reilly/` and `sequence-copy.md` under `processes/outbound/` because they're referenced widely + in the decision log; ownership moved, the paths didn't. (If a future cleanup wants them relocated under `agents/michelle/`, that's an orchestrator call — flagged, not done here.)
- **Split logged** in `decisions/2026-06-15_michelle-split-from-reilly.md`.
