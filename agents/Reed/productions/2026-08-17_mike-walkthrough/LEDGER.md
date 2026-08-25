# yourco — walkthrough video for Mike (2026-08-17)

**Asset:** `yourco-for-mike.mp4` · 1920×1080 · **3:42** · narrated · v3 (+ the business explained up front, + the staged website)
**Ask (the Founder):** "a demo/explainer video walking through the business, the goals, the tools, how it all
works, the CRM, HQ, Connector Console."

## What it is
A narrated screen walkthrough of the **real** surfaces — HQ and the CRM driven headlessly like a user,
on live data. Not generative video, not mockups. Same method as the Property OS demo
(`../2026-08-17_property-os-demo/`), which is the precedent this reuses.

The structural choice: **the honest state is a beat in the film, not a disclaimer at the end.** Scene 8
is a full card of what hasn't happened, and the closing line is "the software is real and the business
hasn't started." That matches how the Founder is running the partner conversations and satisfies the
credibility gate the strongest way available — every frame is the actual software.

## Structure (15 segments)
1. Title card — what yourco is
1b. **The motion** (v3) — Audit → Build → Operate → Expand as a four-step card, ending on the line
    that separates yourco from a vendor: the client never touches a model, a token or a server
1c. **What a client gets** (v3) — the eight pillars, the three shapes a module ships in (named
    employee · headless automation · client-facing product), and the flat retainer with absorbed cost
1d. **The website** (v3) — the real staged site: the home page ridden top to bottom, then `audit.html`,
    the priced front door the whole funnel points at. Stated on camera as **built and not published**
2. **HQ · Today** — the company on one screen; $0 MRR, $24k pipeline, read live
3. **HQ · The Board** — 30 open items; the top three are unflattering and stay on screen
4. **HQ · Partners** — 50/35/15, *not papered*, 0/3 signed, 17 open fills, no counsel
5. **HQ · Agents** — the org chart: 27 AI employees, 16 live, by function
6. **CRM · Today** — 23 open deals, $24,000, win rate "—"
7. **CRM · deal ladder** — 3 actions overdue, 21 deals gone cold at 65 days
7b. **Connector Console** (v2) — the growth engine: where a connector stands, what's waiting on them,
    what yourco says to the people they send. Shot on `_SAMPLE-populated.html`, the fixture — **never a
    real connector's ledger**, which is the whole reason the sample export exists
7c. **HQ · System** (v2) — every sanctioned loop, its cadence, and when it last produced: ON-TIME /
    STALE / UNTRACKED, counted from committed artifacts. Most ran the morning of the shoot, which is
    also the evidence the 12-day pause actually ended
7d. **Slack control surface** (v2) — a labelled *diagram* of the 26 per-agent channels + `#all-yourco`,
    the two-way command path, and the gate that still denies send/delete/shell. Marked "Not a
    screenshot" on the card, because it is the one frame in the film that isn't
8. Honest-state card — the full ledger of what hasn't happened
9. End card — "The software is real. The business hasn't started."

## Pipeline (repeatable)
- **Capture:** `puppeteer-core` + system Chrome headless → `page.screencast()` per scene
  (`capture.mjs`). Injected brass cursor dot so the eye follows the click. 1600×900 @ 2× DPR.
- **Cards:** `cards.mjs` renders brand cards (indigo `#0F1226`, brass rule, Georgia) at 2× and
  screenshots them — typography instead of ffmpeg `drawtext`.
- **VO:** Higgsfield `text2speech_v2`, **elevenlabs** variant, preset voice **Dylan**
  (`b847bc29-…`) — the voice the Founder picked for the Property OS demo. **15 lines**, `atempo 1.06`,
  250 ms lead-in. Two of the first nine hit a 429 and were resubmitted; check `submitted_count`.
- **Assembly:** ffmpeg — each scene `tpad`-frozen to its narration length + 0.7 s breath, then
  concat. No music; VO-only, matching the educational read.

## Capture bugs, found on QA frames
1. **The Melanie chat panel (`#mel`, fixed 360×430) covered the right column of every HQ door.** Hidden
   via injected CSS for capture — it is a live control, not content. Found on a frame, not by eye.
2. **The CRM sidebar is scroll-nav, not a view switch.** Coordinate clicks *and* `el.click()` both left
   the pane on "1. Today" while the cursor sat on "Pipeline" — so scene 7 was re-shot as a scripted
   scroll down the deal ladder (`recap7.mjs`), which shows more anyway.

## Honesty & brand checks
- Every number on screen is the live system's; nothing was staged or seeded for the film.
- No fabricated metrics, no invented traction — the honest ledger is a titled scene.
- Brand: indigo/brass/cream, lowercase `yourco`, all text as rendered overlay (never model-drawn).
- Internal asset. Not white-label, not external — it names yourco and the three members throughout.

## QA
- Audio: mono AAC 44.1 kHz present end-to-end; **0 silence gaps > 2.5 s** (would indicate a dropped
  VO line).
- Duration 222 s (v3); every segment paced to its own line rather than a fixed cut.
- The console scene uses the sample fixture by deliberate choice — a real connector's referrals and
  earnings are their private data and do not belong in a film shown to a third party.

---

## v4 — 2026-08-18 · all equity/membership content removed (the Founder)

**Why:** the Founder is having the equity conversation with Mike in person. Nothing about membership should
reach him through a video first. Duration **3:14** (was 3:42).

**Cut entirely**
- **Scene 4 · HQ Partners** — the whole door: the split, "not papered", 0/3 signed, 17 open fills.
  Its VO line is dropped with it.
- **Scene 3 · HQ The Board** — not for the open-items list, which is fine, but for two things inside
  it: the per-owner filter chips (which name Partner B and Mike as owners) and the "Needs a partner"
  callout reading *"Partner B and Mike own none of it yet."* Neither shows a percentage, and both still
  presume the partnership.

**Re-shot**
- **Scene 2 · HQ Today** — the previous take scrolled far enough to reveal the "Needs the Founder" panel,
  which carries *"the OA now needs the Founder BEFORE counsel."* Re-shot at a **1600×660 viewport** so that
  panel sits below the fold entirely, then padded onto the indigo canvas. No DOM hiding needed.

**Verified clean rather than assumed**
- The remaining CRM panes (Today, the deal ladder) **cannot** show the members: Partner B, Michael
  Partner C and Sample Contact have contact records but **no deals**, so they never render in a
  pipeline view. Contacts and Internal were never captured.
- Agents, console (sample fixture), loops, Slack card and all title cards carry no membership content.
- What *does* remain on screen: the sidebar nav item reading **"Partners 7/14"** in the HQ scenes.
  That is a door label plus lock-run progress — no names, no percentages, and it reads as business
  partners. Flagged to the Founder rather than removed, since hiding one nav row in some scenes and not
  others would look odder than leaving it.

**A tooling note worth keeping.** `page.screencast()` silently writes a **0-byte** file if the page is
clicked, or if injected CSS collapses the layout, before recording starts. Three takes were lost to
this. The reliable shape is: `goto` → one small `evaluate` → `screencast()` → drive the page. To reach
a specific HQ door without clicking, use its **deep link** (`/#board`).
