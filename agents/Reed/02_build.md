# Reed — Stage 2: Build

## Build approach
Reed v0 is built from Cowork primitives + a media tool stack. It's YourCo's first *content-production* employee, so it contributes a different set of patterns to `yourco-template` than Atlas (synthesis) or Reilly (outbound pipeline): asset registration, a creative approval gate, and a "show real behavior" credibility gate.

> **Model note (2026-08-24):** **Seedance 2.5** is live on Higgsfield (shipped 07-31, API 08-07) —
> **30s single-pass** generation (vs ~5s), a 3-minute long mode, timestamped editing, and up to 50
> reference assets. Same vendor, same lock, so no decision is needed. It targets the pipeline's real
> cost, which is *assembly*: stitching 5s clips and holding identity across them. **Switch the
> default and report the first render's credit cost** before it becomes standard.
> Triage: `loops/_triage/2026-08-24_batch-ten.md`.

## Production standard v3 — concept-first, premium AI (LOCKED 2026-06-22) ⭐ READ FIRST
The default for **hero / brand / explainer pieces** (and the quality bar for everything). Born from the home-explainer miss: pretty AI clips with no idea looked "$500," felt generic, and didn't communicate yourco/the AI OS. The fix is the *idea and the craft*, not the resolution. Decision: `decisions/2026-06-22_Reed-premium-concept-first-video.md`. Worked example: `agents/Reed/productions/2026-06-22_home-explainer-v2-concept.md`.

1. **Concept before a single clip.** No generation until there's a written **concept/treatment**: ONE central metaphor + an **ownable visual signature** (a consistent visual language carried across every shot) + a storyboard. Random beautiful shots with no idea = the failure mode. Reed creative-directs; the Founder signs off on the *concept* first.
2. **It must communicate.** Every piece has to make a first-time viewer *understand yourco + the AI OS* — through **concrete imagery** (a real owner, the business, the outcome). **Abstract glowing-particle loops are banned as the primary visual** — they read as generic AI and explain nothing.
2a. **Tone = grounded, real, premium (LOCKED 2026-06-23).** Believable real-world business; the "AI OS" meaning carried by **VO + designed overlays + only a subtle warm glow** — NOT sci-fi light. **Ruled out (don't repeat):** theatrical/sci-fi light-beams (too much), literal humanoid agents (uncanny gold androids), calm static office (boring), "exciting"→crowd (reads as a party). **Energy comes from MOTION + EDIT + MUSIC**, not a single dramatic frame: bold kinetic camera moves (not slow drifts), fast rhythmic cuts, a driving bed, a hook in the first 3 seconds. A calm premium frame feels electric once it moves + cuts to music.
3. **Image-first pipeline (the quality unlock).** Design each key frame as a **premium STILL first** (FLUX / `nano_banana_pro` / Higgsfield image) — lock composition, light, brand palette — **then animate** the approved still. Never blind text-to-video for hero work.
4. **Top models only for finals.** Animate with **Veo 3.1 (`veo3_1`, quality `high`/`ultra`)** or **Higgsfield Cinema Studio 3.0 (`cinematic_studio_3_0`)**; **Kling 3.0 full** (`kling3_0`, pro/4k) for multi-shot. **Kling Turbo / 720p = rough drafts only.** Finals: **1080p, 16:9**. **All generation runs through the Higgsfield MCP — the sole engine; OpenMontage dropped 2026-06-23 (`decisions/2026-06-23_Reed-higgsfield-not-openmontage.md`).** Assembly + VO + text overlays in Descript.
5. **Brand-locked.** Midnight Indigo `#161B33` · Brass `#B8965A` · Cream `#F4EFE6`; lowercase `yourco`. All text/wordmark/CTA are **post overlays** (Descript/AE) — never AI-rendered (see the hard rule below).
6. **Sample-first + cost discipline.** Produce **one premium proof-of-look frame** for the Founder's approval **before** any batch. Preflight every generation with `get_cost`; log credits. (Higgsfield Plus credits; no per-clip cash.)
7. **Credibility gate unchanged** (`decisions/2026-06-17_Reed-realistic-video-openmontage.md`): represents what yourco will actually build/deliver; no fabricated metrics/results, no fake testimonials/likenesses; pre-revenue → outcomes stay qualitative. Kolby evals → the Founder approves before anything ships.
8. **Name the gotcha moment (added 2026-07-24, `decisions/2026-07-05_tool-triage.md` §Addendum 07-24).** Before production, every demo/explainer/embedded-surface piece names its **gotcha moment**: the ONE capability, shown in ≤5 seconds, that conveys the entire thesis with zero explanation (Design Studio: photo → instant range; storm-verify: storm hits → verified SMS; front desk: 9:42pm call → booked job). The first 5 seconds of the piece carry it; secondary features never lead. If the concept can't name its gotcha moment in one sentence, the concept isn't ready.

> The v2 cold-outreach arc below still governs *per-prospect demo* structure; v3 governs *craft + medium + the concept-first discipline* on top of it.

## Standing video structure (v2 — locked 2026-06-08)

Every Reed cold-outreach demo follows the same **3-part story arc**. This mirrors the structure of Reilly's Email 1 (poke the bear → paint Nirvana) so the email and the video reinforce each other.

### The arc (60–90 sec total)

| Part | Duration | Job | What's shown |
| --- | --- | --- | --- |
| **1. The problem** | 10–15 sec | Open on the prospect's reality. Visual recognition before any explanation. | 2-3 problems the owner/buyer has normalized — phone ringing during workday, work piling up, manual chaos. No voiceover required; the visual does the work. |
| **2. The agent in action** | 35–50 sec | Show, don't tell. The agent doing the actual work end-to-end. | Screen capture of a real YourCo digital employee handling the use case from input to outcome. Real workflow, real outputs. Quiet, demonstrative. |
| **3. The outcomes** | 10–15 sec | Land on what life looks like because the agent did the work. | 2-3 visual outcomes: the calendar fills itself, the owner is back on-site, the work that used to live in the owner's head is now somebody (something) else's job. |

### Standing end-frame requirement
Every cold-outreach demo ends on the same clean visual: **"Live in 48 hours from signed agreement."** No other CTA on screen. The email signature handles the rest. This anchors YourCo's time-to-deploy promise consistently across every campaign.

### Why this arc
- **Structural parity with Email 1.** The video and the email reinforce the same arc. The prospect sees the problem named in text on Monday, then sees the problem and its resolution on screen on Friday.
- **Commission-breath-removal.** The video sells nothing — it shows. Removing voiceover salesmanship is the same posture Reilly's copy uses. Quiet authority over loud claims.
- **Reusability.** Same arc fits every vertical: surface the vertical's specific pain in Part 1, swap in the vertical's specific agent in Part 2, swap in the vertical's specific outcomes in Part 3. Script changes per vertical; structure stays constant.

### Tone rules (enforced by Luka)
- No voiceover salesmanship. Quiet, demonstrative. Let the workflow speak.
- Real agent, real workflow. Not a mockup. Not a Figma frame.
- Lowercase `yourco` wherever the wordmark appears.
- No buzzwords in on-screen text (forbidden list lives in `/brand/v0/brand-guidelines.md`).
- No hype emoji on screen.
- End-frame is quiet — no "BOOK NOW" or "GET STARTED" or similar. Just the 48-hour line.

## Hard rule: never let the AI render text (learned 2026-06-10)
AI video models (Higgsfield / Seedance) render any text — letters, words, numbers, signage, UI labels — as **illegible gibberish**. It always looks bad and breaks the credibility gate. So:
- **Generation prompts must hard-forbid ALL text:** *"absolutely no letters, no words, no numbers, no readable text, no labels, no signage anywhere."* Show screens, calendars, papers, nameplates, dials, and notifications as **blank, or as abstract icons / dots / shapes / color blocks only** (the phrasing the landscaping demo used successfully — not the weaker "no on-screen text").
- **Any real text — the end-frame line, the wordmark, captions — is added in POST** (Descript / Canva) as crisp, real text. **Never generated into the clip.**
- A rendered scene showing any baked-in word or number **fails QA and is re-rendered.**
- *Origin:* the 2026-06-10 explainer + generic batch rendered gibberish text in the screen/calendar/nameplate scenes; re-rendered text-free with the hardened prompt.

## Methodology alignment (Reilly v2)
Reed's video is **Email 2 of Reilly's 3-email + 3-SMS sequence** (see `/agents/reilly/copy-structure.md`). Every Reilly campaign requires a Reed asset before it can launch. This makes Reed load-bearing for outbound — the campaign artifact files an asset request before staging in Instantly.

Reilly's request lives at: `/agents/Reed/requests/<date>_<vertical>_email2-demo.md` (use `_TEMPLATE.md` as the starting structure).

## Production pipeline
```
[vertical + use-case + pain to dramatize]
      │
      ▼
1. BRIEF ──────────► strong model → script / storyboard (≤ 60–90s)
   gate: claims match what YourCo can actually deliver (human-in-loop)
      │
      ▼
2. WORKING DEMO ───► build/script a minimal real agent doing the task
   gate: 0 fabricated capabilities — only capture what actually runs
      │  → screen capture
      ▼
3. VOICEOVER + ────► ElevenLabs-class VO + templated assembly
   ASSEMBLY          (screen capture + captions + intro/outro)
      │  → final cut (draft, unpublished)
      ▼
3.5 VISION-QA ─────► run .claude/skills/visual-brand-qa/ on the stills/keyframes
   gate: binary pass/fail vs brand/DESIGN.md (palette · one-brass · type ·
   NO AI-rendered text · idioms · credibility · premium bar) — fix fails
   BEFORE routing to the Founder (added 2026-07-29, Isenberg/Schneider steal)
      │
      ▼
   [HUMAN-MUST-APPROVE] ── the Founder reviews final cut ──► publish
      │
      ▼
4. PUBLISH ────────► hosted landing page + animated thumbnail/GIF + tracked link
      │
      ▼
   REGISTER asset (vertical → page URL + thumbnail + link) ──► available to HERMES
```

## Tool stack (relocked 2026-06-09 — Higgsfield supersedes Canva for animation; see `/decisions/2026-06-09_Reed-higgsfield-animation-stack.md`)

**Reed's demos are animated only — no real working agent capture, no AI voices, no live B-roll.** Direction (the Founder 2026-06-09): fully animated + conceptual — show what the agents look like from a *workflow* standpoint (problem → agent at work → outcomes), not realistic humans or literal product UI. **This is Reed's job to run** (Higgsfield is an available MCP tool).

| Layer | Vendor | Notes |
| --- | --- | --- |
| **Script** | Strong model | Quality + accuracy of claims |
| **Animation (the engine)** | **Higgsfield** (MCP) | Generates animated, conceptual workflow scenes. Default Seedance 2.0 (reference-driven, consistent identity, silent); Veo 3.1 / Kling 3.0 for specific shots. ~22–25 credits per ~5s 720p clip. Lock a character + palette via a reference frame for consistency across scenes. |
| **Brand kit + captions + assembly + end frame** | **Canva Pro** ($15/mo) | Retained for the brand kit (Midnight Indigo + Cream Linen + Brass + lowercase wordmark), caption overlays, stitching the Higgsfield clips, and the cream/indigo/brass end frame. No longer the animation engine (its AI deck-to-MP4 read as slides). |
| **Voiceover** | None — silent + on-screen captions | Workflow speaks. Captions added in post — never baked by the generator (AI text is unreliable). |
| **Hosting (landing page + tracked link)** | Loom (free) | Upload final MP4; Loom handles landing page + tracked URL natively. |
| **GIF preview** | Canva / editor export (3-5 sec loop) | The most arresting cut, ≤2MB. |

**Monthly recurring:** $15/mo Canva + Higgsfield credit usage
**Per-demo variable:** ~300 Higgsfield credits for a full ~14-scene set (~22–25 credits/clip)

### Candidate tools (from the DesignJoy/Brett interview — the Founder sets up if wanted, 2026-06-17)
The **motion** stack is locked (Higgsfield, `decisions/2026-06-09_Reed-higgsfield-animation-stack.md`) — don't churn it. But Brett's toolset surfaced one genuine gap-filler + two alternates, all *static-image* tools that complement (not replace) the animation engine. Agents can't create accounts/keys — these are **the Founder's to set up** if he wants them; flagged here so they're a decision, not a surprise.
- **Nano Banana Pro** (Google's image model) — **recommended add.** Best-in-class for *specific* static shots: a model/person holding a product, clean product imagery, realistic scene composition. Fills yourco's one real gap — high-quality **static** brand/marketing imagery (blog headers, social stills, iconography, supporting assets) that Canva can't generate and Higgsfield (motion, illegible text) shouldn't. Cheap, high ROI for Katie's social + Webb's site imagery. *Note: still respect the "real text in post" rule — generate the image, add any text crisply afterward.*
- **Krea (krea.ai)** — alternate/aggregator: one subscription that fronts many image+video models. Useful if the Founder wants a single console instead of per-model accounts; otherwise skip.
- **Midjourney / Runway** — Brett's go-tos for stylized artwork / video gen. Overlap with Higgsfield (video) and Nano Banana (image); **not needed** given the locked stack — listed only for completeness.

Adopt-now-free (no account): the **meta-prompting + rule-sheet** practices (`learnings/ops/2026-06-17_meta-prompting-and-rule-sheets.md`) — have an LLM write the tool-specific generation prompt, and keep a saved Reed rule sheet (character/palette/motion/text-in-post) every shot inherits.

### What's NOT in Reed's stack (and why)

- **Vapi** — still locked as YourCo's voice agent platform for *paying client voice deployments* (not used in demos). Deferred spend until first paying voice client.
- **Descript** — replaced by Canva. Canva handles animation + assembly + export in one tool.
- **Storyblocks / Pexels** — not needed; videos are animated, not live B-roll composites.
- **Twilio + ElevenLabs** — no real calls in demos; no AI voice work needed.

### Credibility gate (updated for animation)

Original: "0 fabricated capabilities — show only what actually runs."
**Updated:** "Animated faithfully — every workflow shown represents what YourCo will actually build for a client."

The honesty bar moves from *literal real capture* to *accurate illustration of the real product*. This is how good B2B explainers work — illustrated, specific, and accurate to what gets shipped. Animated UIs of the agent's intake dashboard, qualification flow, calendar event, and SMS confirmation are honest if they reflect what the real Vapi-based agent actually does for a paying client.

## Pattern reuse — every animated video becomes the next demo's foundation
The first Canva project ("GreenLine Landscaping intake demo") becomes the reusable template. Next vertical: duplicate the Canva project, swap the vertical-specific illustrations (Part 1 problem scenes), tweak the workflow specifics (Part 2 qualification fields), update the outcomes (Part 3). The brand kit, end frame, motion patterns, and structural beats are all reusable.

## Patterns reused from Atlas / Reilly
- **Approval summary delivery** (artifact + Gmail draft + Slack) — same primitive.
- **Closed-loop feedback section** on each production record.
- **Watchdog-trigger format** — standardized.
- **Cross-employee interface** — Reed is the supplier side of the Reilly→Reed asset request established in Reilly 02_build.

## New patterns Reed contributes to yourco-template
- **Asset registry** — a vertical→asset lookup other employees query (reusable shared-asset pattern).
- **Creative approval gate** — human-must-approve before publish, with a staged unpublished draft.
- **Credibility gate** — "show only real, running behavior" — reusable for any client-facing demo/content.

## Definition of done — an asset nobody saw did not do its job (added 2026-08-25)

Publishing is not the finish line. **When an asset is put in front of a prospect, register it on
their deal in the CRM** — the deal dossier's *+ artifact*, `type: video`, status `shown` (or
`reacted`, with what they said).

Why this and not a view count: Reed's owned number was re-scoped on 2026-08-25 from *"assets that
appeared in a **won** deal"* — which graded a production agent on whether the Founder closes — to **reach**,
which is the boundary of what Reed controls. What happens after the prospect watches it is the
sales agent's number. Production volume is activity; reach is the outcome.

- **`built` deliberately does not count.** A video sitting in the registry has not reached anyone.
- The denominator is the **published** rows in `_asset_registry.md`, so an unpublished script is not
  held against the number.
- Today it reads *refused*, not 0%: three assets are published and **not one is registered on a
  deal**, so a 0% would claim the linking habit exists and failed. It does not exist yet, and both
  channels that would carry these — Reilly's Email 2 and the site — are behind the launch-gate.
  A video shown on a call is not gated, and is the fastest way this number becomes real.

## Build status
- [ ] Demo script/storyboard template written
- [ ] Media tool stack selected (VO, assembly, hosting) + logged in decisions
- [ ] First working demo identified (candidate: Atlas producing a Monday briefing — already real)
- [ ] Asset registry file created (vertical → URL + thumbnail + tracked link)
- [x] First reusable per-vertical demo produced + approved + published — **landscaping intake demo, the Founder-approved 2026-06-09** (Higgsfield + Descript). https://share.descript.com/view/L6EdW0JYGQJ
- [ ] Reilly wired to request/pull the asset for touch 2
- [ ] `contact@yourco.example.com` provisioned (manual — the Founder, not blocking v0)
- [x] **Assembly automated (Descript MCP).** Stitching the Higgsfield clips + captions + end frame + scene timing now runs through the Descript MCP (`prompt_project_agent` → `publish_project`). This replaced the manual Canva stitch.
- [ ] **AI-voice rendering (the one remaining manual touch).** Generating the spoken VO is NOT cloud-automatable in this setup: ElevenLabs' MCP is local-only, and Descript's MCP assembles the project but does **not** expose AI-voice/TTS rendering — it queues the script as `<scratch>` and needs the Descript **app** to assign a speaker. So today the VO requires one manual step (open the Descript project → assign a calm male AI voice → it renders). **To close the gap:** a cloud-callable TTS-rendering MCP/API for Reed — Descript exposing speaker assignment via MCP, a hosted ElevenLabs MCP, or an always-on runtime with TTS API access. Everything else (animation via Higgsfield, assembly via Descript) is automated. See `/decisions/2026-06-09_Reed-higgsfield-animation-stack.md`.

## Autonomy
Governed by the standard in `processes/autonomy-matrix.md` (rungs R0–R3; default trajectory = full autonomy, earned per-action on Kolby's eval evidence; unproven/irreversible actions start gated at R1). Reed's actions mapped to rungs:

| Action | Rung | Notes |
|---|---|---|
| Read briefs/requests, write concept/treatment + storyboard, research | **R3** | inherently safe |
| Asset production — generate stills/clips (Higgsfield), assemble (Descript), stage an **unpublished** draft, register the asset, post internal `#yourco-Reed` notice | **R3** | internal/reversible; Higgsfield Plus credits (no per-clip cash) |
| **Publish** — push a final cut public (Loom landing page / tracked link) or hand it to external outreach | **R1 (hard floor)** | the Founder reviews the final cut and commits; credibility gate (no fabricated capabilities/metrics) + creative approval gate |
| Spend > $1 (cash media spend) | **R1** | human-in-loop |

**Hard-floor / gated:** publishing (and use in external outreach) stays at R1 — the Founder approves every final cut by design; the concept also gets the Founder sign-off before batch generation. Internal production is fully autonomous (R3).

## Known overlay decisions
- **v0 runs under the Founder's identity** until `contact@yourco.example.com` exists (same as Atlas/Reilly v0).
- **First demo should reuse a real YourCo agent** (e.g., Atlas) so the credibility gate is trivially satisfied — fastest path to a publishable asset.
- **Reusable-before-personalized.** No per-prospect video until reusable per-vertical demos prove they lift reply rates in Reilly.
