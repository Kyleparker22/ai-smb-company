# Reilly — Stage 2: Build

## Build approach
Like Atlas, Reilly v0 is built from Cowork primitives (MCP connectors + LLM calls + workspace files + a scheduled/triggered task) rather than from `yourco-template` (which doesn't exist as code yet). Reilly is the second source of template patterns — especially the multi-stage pipeline-with-gates pattern that Atlas (a single synthesis step) doesn't exercise.

## Architecture — staged pipeline (updated 2026-06-07 for multi-source sourcing)
```
[the Founder: "vertical = X" + ICP + filters]
      │
      ▼
1. MULTI-SOURCE SOURCING (run in parallel, per Polo's source set for the vertical)
   ┌───────────────┬──────────────────┬─────────────┐
   │ Outscraper    │ Instantly        │ Vibe        │
   │ (Google Maps) │ SuperSearch      │ (Explorium) │
   └───────┬───────┴────────┬─────────┴──────┬──────┘
           └────────────────┼────────────────┘
                            ▼
   Normalize → Dedup (domain → phone → name+city) → Merge with source[] tag
   gate: dedupe vs suppression list + ICP-fit filter + coverage-test threshold
      │  → canonical merged lead list with cross-source confidence tags
      ▼
2. RESEARCH/ENRICH ────► web scrape/fetch + Gemini Flash synthesis
   gate: every data point traces to a source (no hallucinated facts)
      │  → research card per prospect (3–5 points + 1 pain hypothesis)
      ▼
   [request 1 demo asset for vertical X] ──► PARTNER_BON (Email 2 video)
      │
      ▼
3. COPYWRITING ───────► MICHELLE owns this step (split 2026-06-15) — Reilly hands the vertical + target research; Michelle writes
   - v2 commission-breath-removal methodology
   - 3 emails + 3 SMS, 21 days (see /agents/reilly/copy-structure.md — owner Michelle)
   - Email 1: poke the bear + paint Nirvana (operational + financial outcomes)
   - Email 2: Reed-produced demo video (animated GIF → Loom)
   - Email 3: reframe + sharper Nirvana + low-pressure release
   - SMS 1, 2, 3: reference prior email + Calendly + STOP
   - Standing claim: "Live in 48 hours from signed agreement"
   - Pricing pulled from cold; CTAs in the Founder's signature only
   gate: Luka brand review, claims check, outcome-framed
      │  → staged sequences
      ▼
4. ORCHESTRATION ─────► Instantly API (runtime/instantly.py): create campaign + load the paused
      │                   4-touch sequence (`--create`, DRAFT/PAUSED, no activate path), push leads
      │                   (`--stage`), promote warm replies → CRM (runtime/promote.py). DO NOT LAUNCH.
      │  → approval summary to the Founder (Gmail draft + Slack)
      ▼
   [HUMAN-MUST-APPROVE] ── the Founder approves ──► launch
      │
      ▼
   webhooks: replies / bounces / opens ──► feedback to stage 1 (suppression + ICP refine)
```

## Tool stack (see decision log 2026-06-07_outbound-sales-stack — including the same-day amendments: SMS channel, coverage-test pivot, and the multi-source sourcing architecture that supersedes primary-source-per-vertical)

- **Sourcing — multi-source per vertical (Polo decides source set; Reilly runs all approved sources in parallel, dedupes, merges):**
  - Trade/services SMB (landscaping, roofing, hardscaping, plumbing/HVAC) → **Outscraper + Instantly SuperSearch + Vibe Prospecting** (all three, dedupe-merge)
  - White-collar / knowledge work (law, wealth, insurance, professional services) → **Vibe Prospecting + Instantly SuperSearch** (skip Outscraper; Google Maps weak for these)
  - Hyper-local single-metro → **Outscraper + Instantly** (Vibe optional)
  - Each merged prospect carries cross-source match tag: `single-source`, `two-source`, or `all-three`. Cross-source match = confidence signal; campaigns lead with `all-three` records.
- **Enrichment (all verticals):** Vibe Prospecting (Explorium MCP) — still the per-company research layer (firmographics, technographics, funding, tech stack) after sourcing.
- **Research synthesis:** Gemini Flash (cheap/fast) reads company site + news, extracts pain points. Token economics: Flash for volume research, strong model only for copy.
- **Copy:** strong model, per-prospect sequence generation.
- **Sending (email + SMS):** Instantly Hyper CRM tier ($97/mo) — API + webhooks (observability/feedback), unlimited inboxes (flat cost; scales into client tenants in v2), native warmup + deliverability dashboard, integrated 10DLC + SMS sequences.
- **Activation-layer CRM:** Instantly CRM (bundled with Hyper CRM tier) — campaign-active prospects, sequence position, reply/bounce. Bridges to canonical `clients/_pipeline.md` via Reilly's update workflow. See `decisions/2026-06-07_crm-architecture.md`.
- **Fallback (parked):** Clay for waterfall enrichment if Vibe match rates disappoint on knowledge-work verticals (~$149/mo).
- **Dropped:** Apollo (cancelled 2026-06-06; stale-data/bounce risk; redundant with Vibe).
- **v1 (committed):** Outscraper pilot within 30 days for local-trade Google Maps coverage; Leadbay after first 3–5 closed deals.

## Patterns reused from Atlas
- **Triple/■ delivery for the approval summary** (artifact + Gmail draft + Slack) — same primitive.
- **Scheduled-task-as-launcher** — a thin trigger loads the SOP + ICP, then runs.
- **Closed-loop feedback section** — "What I'd do differently next run" on each campaign artifact.
- **Watchdog-trigger format** — standardized across engagements.

## New patterns Reilly contributes to yourco-template
- **Multi-stage pipeline with per-stage eval gates** (Atlas is single-stage; Reilly is the first multi-stage employee).
- **Hard human-must-approve gate on external action** (send) with a staged-but-unlaunched artifact awaiting approval.
- **Hallucination gate** — "every claim traces to a source" as a reusable enrichment check.
- **Cross-employee request** — Reilly → Reed asset request (first inter-agent dependency).

## Build status (current as of 2026-06-08)
- [x] **Copy methodology v2 written** — `/agents/reilly/copy-structure.md` (commission-breath-removal)
- [x] **Vibe Prospecting (Explorium) MCP connected** at `https://vibeprospecting.explorium.ai/mcp`
- [x] **Vibe coverage test ran** — landscaping returned ~25-50 Vibe / ~500 Instantly hits → led to multi-source pivot (Outscraper + Instantly + Vibe). Coverage gate now runs every new vertical.
- [x] **Polo pricing lock — landscaping/hardscaping** locked in `/pricing/v0/landscaping-hardscaping.md`. Reilly cannot send into an unlocked vertical.
- [x] **Polo channel selection lock — landscaping** locked: email + SMS approved; LinkedIn + phone deferred.
- [x] **Instantly account** — done-for-you setup via Instantly: `getteamyourco.com` is the cold-email domain, 2 mailboxes provisioned, warmup running (ETA cleared ~2026-07-08).
- [x] **Instantly Hyper CRM tier upgrade ($97/mo)** — done. SMS as channel 2 unlocked.
- [ ] **10DLC brand + campaign registration** — submitted; orphaned Twilio bundle conflict. **Status corrected 2026-06-09:** Instantly support replied (via their Messenger/Intercom) and followed up 2× (latest 06-09) — the ball is in **the Founder's court**, not Instantly's. Action: the Founder reads Instantly's message in the support chat (resolution steps for the bundle conflict are there), then sends the chase reply drafted in Gmail (fold in answers to whatever they asked). NOT waiting on Instantly.
- [x] **Multi-state SMS suppression list locked** — FL, WA, OK, MD, NY, CA suppressed from SMS sends. Applied at batch time. (the Founder decision 2026-06-08; revisits when Ray legal agent built or multi-state legal review done.)
- [ ] **STOP keyword handling configured** in Instantly — pending campaign launch.
- [ ] **DNC list scrub layer** wired ahead of every batch.
- [ ] **First Reed asset delivered** — landscaping Email 2 video; request filed 2026-06-08, awaiting Reed script.
- [ ] Suppression list file created at `/agents/reilly/_suppression.md`.
- [ ] First campaign launch on landscaping vertical (blocked by 10DLC + warmup + Reed asset).
- [ ] `contact@yourco.example.com` provisioned (manual — the Founder, not blocking v0).

## Autonomy
Reilly is governed by the Autonomy Matrix (`processes/autonomy-matrix.md`) — every action sits on a rung (R0 observe · R1 draft/propose · R2 auto+notify+reversible · R3 fully autonomous); the default trajectory is full autonomy, with autonomy **earned per action on Kolby's eval evidence**, never switched on. New/unproven/irreversible actions start gated.

| Action | Start | Ceiling | Advance when |
|---|---|---|---|
| Source / enrich / dedup / coverage-test (internal, reversible) | **R2** | R3 | Kolby eval record — clean sourcing runs (0 ICP/suppression leaks) → R3 |
| Stage a campaign **paused** in Instantly (unlaunched, reversible) | **R2** | R3 | clean staged-campaign track record (conforms to copy-structure, all gates pre-checked) → R3 |
| Research synthesis / write research card (internal) | **R3** | R3 | inherently reversible (git) |
| Workspace file writes, Slack post to `#yourco-reilly` | **R3** | R3 | reversible |
| **Send / launch a campaign** (email + SMS to prospects) | **R1 (gated)** | R2\* | climbs to R2 (auto + notify + reversible window) **only** on Kolby's eval-vs-reality record + the Founder's threshold; deliverability-gated throughout |

\* **Capped ceiling.** Sending into a client's customers/prospects never reaches unattended R3 without a named exception + counsel — YourCo is not the sender-of-record and CAN-SPAM/TCPA/FTSA + deliverability risk make this a hard-floor class (`processes/autonomy-matrix.md`).

**Hard floor / gated by design:** sending a campaign requires the Founder's explicit batch approval (the existing hard launch gate) and stays deliverability-gated (warmup health, bounce rate, suppression scrub, 10DLC) — no send climbs a rung while any deliverability watchdog is tripped. Adding a sending domain/inbox and any spend > $1 stay human-in-loop. This is the same earn-it climb yourco sells clients, proven on the runtime's R1 send-floor first (`runtime/autonomy-matrix.md`).

## Channel stack (per amendment 2026-06-07)
- **Email** — primary, via Instantly. Universal across verticals.
- **SMS** — channel 2, via Instantly Hyper CRM. Per-vertical: fits landscaping/roofing/hardscaping/real-estate/plumbing-HVAC; does NOT fit law/wealth/insurance.
- **LinkedIn** — channel 3 (v1, not v0). Per-vertical.
- **Phone call** — channel 4 (v1, not v0). Per-vertical.

Channel selection per vertical is a Polo decision, landed in `/pricing/v0/<vertical>.md` under "Channels". Reilly cannot use a channel not in that section.

## Stack roadmap (per decision log amendment 2026-06-07)
- **v0:** Vibe + Gemini Flash + strong-model copy + Instantly (current).
- **v1 (Q4 2026 target):** Layer Leadbay predictive ICP scoring on top of Vibe-sourced lists once won/lost data exists.
- **v2 (only if needed):** Add Clay for complex multi-step enrichment workflows Vibe can't express.

## Known overlay decisions
- **v0 runs under the Founder's identity** until `contact@yourco.example.com` exists (same as Atlas v0).
- **Sending infra is a hard prerequisite.** Stage 4 cannot go live until the cold-email sending domain (`getteamyourco.com`, separate from `yourco.com` primary) finishes warmup. Never send from `yourco.com` primary.

## Hard launch gates (all must clear before any send)
Every campaign launch requires every gate below to be ✅. Reilly stages but does not launch until all clear.

1. ✅ **Polo pricing lock** for the campaign's vertical (`/pricing/v0/<vertical>.md`)
2. ✅ **Polo channel selection lock** for the vertical
3. ✅ **Copy-structure v2 conformance** — campaign artifact follows `/agents/reilly/copy-structure.md` exactly
4. ✅ **Luka brand review passed** on the campaign artifact (voice fixes applied)
5. ✅ **Reed asset delivered + registered** in `/agents/Reed/_asset_registry.md` — Email 2 cannot ship without it
6. ✅ **the Founder approves the campaign** (separate from batch approval)
7. ✅ **the Founder approves the batch** (sourced prospect list)
8. ✅ **State suppression applied** at batch time (FL, WA, OK, MD, NY, CA suppressed from SMS per the Founder 2026-06-08 decision)
9. ✅ **10DLC brand + campaign approved** for SMS sends
10. ✅ **Warmup health-gated low-volume start** — cold sends may begin once `getteamyourco.com` warmup metrics are healthy (~90%+ inbox placement), at ≤10/inbox/day with warmup continuing underneath; full-volume scale-up waits for full warmup. (Amended 2026-06-09 — see `/decisions/2026-06-09_reilly-early-warmup-ramp.md`. Supersedes the prior "warmup complete (~July 8)" gate.)
11. ✅ **Suppression list scrub** — DNC + prior-replied + state-suppression run before push to Instantly
