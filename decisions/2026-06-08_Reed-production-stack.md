# Decision: Reed's Production Stack (and YourCo's AI Voice Agent Platform)

**Date:** 2026-06-08
**Owner:** the Founder, advised by Reed + Luka
**Status:** Locked (with same-day amendment below — Reed's production stack simplified to animated-only)

---

## AMENDMENT 2026-06-08 (same day, post-original decision)

**What changed:** Reed's production stack simplified. Videos are animated only — no real working agent capture, no AI voices, no Vapi sandbox build. The Vapi platform decision for paying client voice deployments **stands** — it's just not used in Reed's demos.

**New Reed production stack (replaces the table below for Reed specifically):**

| Layer | Vendor | Cost |
| --- | --- | --- |
| **Animation + brand kit + assembly + export** | **Canva Pro** | $15/mo |
| **Hosting** | Loom (existing free tier) | $0 |
| **Brand kit baked in** | Midnight Indigo + Cream Linen + Brass + lowercase wordmark | included in Canva |

**Dropped from Reed's stack:** Vapi, Descript, Storyblocks, Pexels (no live B-roll needed), Twilio number (no real call), ElevenLabs voices (no AI voice).

**New monthly recurring:** $15/mo (Canva Pro only). Down from original ~$45/mo planned.

**Credibility gate evolution:** Original rule was "0 fabricated capabilities — show only what actually runs." Updated for animation: **"animated faithfully — every workflow shown represents what YourCo will actually build for a client."** Honest illustration of the real product, not screen capture of a running agent. This is how good B2B explainers work — illustrated, specific, and accurate to what gets shipped.

**What stays from the original decision:**
- Vapi is still locked as YourCo's AI voice agent platform — **for paying client voice/intake deployments** (when Janice → Kimi delivers an engagement involving a phone agent). Just not used in Reed's demos.
- The 3-part story arc + 48-hour-from-signed-agreement end frame are unchanged.
- Reed's approval gates (script approval, final cut approval, register-before-publish) are unchanged.

**Why the simplification:**
- 67% lower monthly recurring cost ($15 vs $45)
- No sandbox build = days of work removed from production timeline
- No real call recording = no the Founder recording session needed
- Animation can be polished and on-brand by design — better executive-trust aesthetic for YourCo than potentially rougher real capture
- Reed iterates faster per vertical — swap illustrations, not rebuild a sandbox agent
- Vapi spend deferred until first paying voice client (when it generates revenue, not cost)

---

## ORIGINAL DECISION (now superseded for Reed — preserved for context and for future client voice deployments)

## What was decided
Reed's production tool stack is locked. Per the principle "pick once, reuse forever" — these tools serve every future Reed production across every vertical Reilly campaigns into.

| Layer | Vendor | Cost | Notes |
| --- | --- | --- | --- |
| **AI voice agent (telephony)** | **Vapi** | ~$0.05–0.10/min usage | Beats Bland AI, Retell AI on production-readiness for v0. ElevenLabs voices bundled. |
| **Video editor** | **Descript Creator tier** | $24/mo recurring | AI-powered transcript editing. Reusable. |
| **B-roll source** | **Pexels (primary, free) + Storyblocks (fallback)** | $20/mo standby cap | Pexels first; Storyblocks when free isn't enough. May cancel Storyblocks after first 2-3 demos if Pexels covers. |
| **Voice (caller — Maria)** | the Founder records himself | $0 | A real human is more credible than two AIs talking. |
| **Telephony infrastructure** | Twilio (existing) | bundled w/ 10DLC | Phone number + SMS, both already in place |
| **Screen capture** | Loom (existing) | $0 free tier | Already standard at YourCo |
| **Calendar integration** | Google Calendar API (existing Workspace) | $0 | Existing infra |
| **Landing page host (Loom hosted page)** | Loom (existing) | $0 v0; subdomain in v1 | Fastest path |

**Monthly recurring cost:** ~$45/mo (Descript $24 + Storyblocks $20 + negligible Vapi/Twilio usage at demo scale)
**Per-demo variable:** ~$2-5 in Vapi + Twilio usage

## Why these picks

**Vapi** — production-ready AI voice agent platform, well-documented, ElevenLabs voices built in, supports custom tool calls (which is what we need for the calendar + SMS + CRM workflow). Bland AI and Retell AI are credible alternatives; Vapi wins on developer ergonomics and the breadth of voice options. The vendor we'd actually want a paying client deploying on.

**Descript** — transcript-based editing means Reed can edit by cutting words from a transcript instead of timeline scrubbing. Massive time savings on every future demo. AI features (overdub, room tone, filler-word removal) are exactly the polish layer we need without an editor.

**Storyblocks (standby)** — Pexels is good but inconsistent for specific scenes (e.g., a landscaping owner writing estimates in his truck at 7pm). Storyblocks fills gaps. Kept as a fallback budget rather than primary spend.

**the Founder voicing Maria** — founders sounding like real customers in their own demo is a small touch of authenticity that pays off. Nobody knows it's the Founder. Beats hiring voice talent or using a second AI voice for $0 and 5 minutes.

## The bigger move — Vapi is now YourCo's AI voice agent platform (scope: voice/intake use cases only)

**Important scope clarification:** Not every YourCo client deployment requires a voice/phone agent. Some clients will need text-only agents (email intake, document drafting, scheduling, internal Q&A) that never touch Vapi. **Vapi is locked specifically for voice/intake-based use cases** — when a client needs a phone-answering digital employee, this is the stack.

For voice/intake use cases, Vapi is the platform every YourCo client's intake employee will deploy on, including when Janice → Kimi delivers a paying engagement involving phone work. The "GreenLine Landscaping" sandbox employee Reed stands up for the demo is the **same architecture** every paying client with a voice intake use case will run on.

This locks one foundational technical piece of YourCo's stack — the voice/telephony tier:
- **Voice + telephony:** Vapi (ElevenLabs voices) + Twilio (numbers, SMS)
- **Calendar:** Google Calendar API (or equivalent in Microsoft tenants when client requires)
- **CRM logging:** Configurable per client — for the demo, a simple Google Sheet or Notion page

For non-voice client use cases, YourCo will lock other tier-specific platforms over time (e.g., email-intake stack, scheduling stack, document-drafting stack). Each gets its own decision doc when first selected.

When Kemba (Platform / Template Engineer) is built, the Vapi intake-employee pattern gets extracted into `yourco-template` as the canonical **"Voice Intake Employee v0"** primitive — one primitive among several the template will eventually carry.

## Reusability across the roster (voice/intake use cases only)

| Agent | Uses what part of this stack |
| --- | --- |
| **Reed** | All of it (his production stack) — used on every demo regardless of vertical |
| **Kimi** (when built) | Vapi + Twilio + Google Calendar — **only when deploying a client engagement with a voice intake use case** |
| **Janice** (when built) | Onboards voice-intake clients using the Vapi-based template Kemba extracts; non-voice clients use whichever stack their use case requires |
| **Atlas** | Vapi usage rolls up into per-engagement cost tracking (where Vapi is used) |
| **Charles** | Tracks Vapi spend per engagement in `/finance/expenses.md` (where applicable) |
| **Rafi** (when built — compliance) | Vapi's voice-recording and consent-handling becomes a compliance review surface for voice engagements |

## Approval
the Founder approved all 5 tool decisions in chat 2026-06-08:
1. ✅ Vapi
2. ✅ Descript
3. ✅ Storyblocks (with $20/mo standby cap)
4. ✅ the Founder records Maria's lines himself
5. ✅ Vapi sandbox approach for GreenLine

## Files touched / to touch
- `/agents/Reed/02_build.md` — replace placeholder tool stack with the locked vendors
- `/agents/Reed/productions/2026-06-08_landscaping-intake-demo.md` — production unblocked
- `/CLAUDE.md` — add Vapi to the internal platform section
- `/finance/expenses.md` — when Charles is live, log Descript + Storyblocks monthly + Vapi usage
- Memory — capture the production stack so future sessions don't re-decide

## Revisit conditions
- After 5 Reed demos: evaluate Descript vs alternatives based on actual editing time. Switch if a clear winner emerges.
- After 3 demos: evaluate Pexels-only sufficiency — drop Storyblocks if Pexels has covered every Part 1/Part 3 need.
- After first paid client deploys on Vapi: reassess pricing tier. Vapi's enterprise tier may unlock cost advantages at scale.
- If Vapi raises prices materially or quality drops: Bland AI and Retell AI are the documented fallbacks.
