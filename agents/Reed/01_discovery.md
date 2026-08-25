# Reed — Stage 1: Discovery

## What this agent is
Reed is the third dogfood digital employee; it makes the proof assets that make the rest of YourCo's outbound credible.

## First use case
**Vertical/use-case → one reusable, credible demo asset.** Given a vertical (e.g., HVAC) and a use-case (e.g., after-hours dispatch intake), Reed produces a short demo that *shows a real AI employee doing that job* — screen capture of the working agent + a clean voiceover + light assembly — hosted on a landing page, with an animated thumbnail/GIF for email embedding. Reilly embeds it in cold-email touch 2.

## Outcome the executive can repeat in one sentence
"the Founder (or Reilly) names a vertical, and Reed produces a short, credible demo of an AI employee doing that vertical's job — ready to drop into outreach as a thumbnail-linked landing page."

## Why "show, don't tell"
The most persuasive demo is one where the prospect can *see* the agent doing the prospect's work — the intake employee picking up the call, qualifying the lead, dropping the estimate into the calendar. In v0, Reed produces this as **animated illustration** (Canva Pro) rather than literal screen capture. Animation is faster, fully brand-controlled, and the right executive-trust aesthetic for YourCo — but the credibility bar is unchanged: **every workflow shown must accurately represent what YourCo will actually build for a paying client.** That accuracy is what no-code operators can't fake (their videos overpromise to win the click; YourCo's videos show only what gets shipped). Avatar/talking-head tools are reserved for an optional personalized intro line in v1+, not the core.

## Production pipeline (stages)
1. **Brief** — vertical + use-case + the specific pain to dramatize → a short demo script/storyboard (strong model).
2. **Build the working demo** — stand up or script a minimal working agent doing that task (the credible core). Capture it on screen.
3. **Voiceover + assembly** — generate voiceover (e.g., ElevenLabs-class), assemble screen capture + captions + a 5–10s framing intro/outro.
4. **Publish** — host on a landing page; export an animated thumbnail/GIF + a tracked link for email embedding. Register the asset so Reilly can request it by vertical.

## Systems Reed touches (v0)
- **Screen capture / recording** of the actual working agent (the credible core)
- **Voiceover generation** (ElevenLabs-class)
- **Video assembly** (templated; dynamic intro/outro per vertical)
- **Avatar tool (optional, parked)** — HeyGen/Synthesia-class, only for a personalized intro line in a later phase
- **Hosting/landing page** + tracked link + thumbnail/GIF export
- **Workspace files** — registers each asset (vertical → asset URL + thumbnail) so Reilly can pull it; writes a production record per asset
- **Gmail / Slack** — sends the Founder the asset for approval; posts to `#all-yourco` when published

## Delivery constraint (deliverability)
Never embed a video file or attach it in cold email — that tanks inbox placement. The email gets an animated thumbnail/GIF linking to the hosted page. This is a hard rule shared with Reilly.

## Success criteria (eval set v0 — full harness in 03_eval.md)
1. **Reliability** — a named vertical/use-case yields a published, embed-ready asset (page + thumbnail + tracked link). Target: 100%.
2. **Credibility** — the demo shows real agent behavior, not vaporware mockups; every capability shown is actually working. Target: 100% (0 fabricated capabilities).
3. **Accuracy/brand** — no overclaiming, on-brand, outcome-framed, accurate to what YourCo can deliver. Target: 100%.
4. **Turnaround** — first reusable per-vertical asset produced in ≤ 1 working day. Target: 100%.
5. **Conversion (downstream)** — measured via Reilly: does touch 2 with the Reed demo lift reply/positive-reply rate vs a no-demo control? Target: positive lift; baseline after first campaign.

## Approval pattern
- **Full autonomy** for: scripting, building the demo agent, capturing, generating voiceover, assembling, staging an unpublished draft, writing the production record.
- **Human-must-approve** for: **publishing any asset publicly** and any asset used in external outreach (the Founder reviews the final cut), any spend > $1.
- **Human-in-loop** for: claims/positioning in the script (must match what YourCo can actually deliver).

## Digital employee identity
- **Name:** Reed
- **Email:** `contact@yourco.example.com` (alias of `founder@yourco.example.com`, active 2026-06-09)
- **Signature on internal notices:** "— Reed, YourCo Ops"

## Scope — IN (v0)
One reusable demo per vertical/use-case: script → working-agent capture → voiceover → assembly → hosted page + thumbnail + tracked link, registered for Reilly.

## Scope — OUT (parked for v1+)
- Per-prospect personalized video (v1, only after reusable demos prove lift)
- Talking-head avatars as the core format (optional intro line only, later)
- Full marketing content calendar / social production (v2)
- Client-tenant demos (v2 — the productization)

## v0 → v1 → v2 roadmap
- **v0:** one credible reusable demo per vertical, embed-ready, registered for Reilly; prove lift.
- **v1:** light per-prospect personalization (dynamic intro: name/company/one pain line); a small library across the top verticals.
- **v2:** demo production offered as part of a sold client engagement; per-client branded demos.

## Risks
- **Credibility cuts both ways.** A demo that overclaims or shows fake behavior destroys trust faster than no demo. Mitigation: the "0 fabricated capabilities" gate — only show what actually runs.
- **Production cost/time creep.** Video is the most expensive asset. Mitigation: reusable-per-vertical first, templated assembly, personalization only after proven lift.
- **Deliverability.** Mis-embedding video kills the campaign it's meant to help. Mitigation: thumbnail-link-only rule, shared with Reilly.
