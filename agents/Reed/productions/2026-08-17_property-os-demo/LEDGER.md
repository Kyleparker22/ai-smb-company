# Property OS — demo & educational video (2026-08-17)

**Asset:** `property-os-demo.mp4` · 1920×1080 · 3:11 · v5 (+ availability scheduling)
**Ask (the Founder):** "a demo & educational video of the Property Manager app getting used and explained."

## What it is
A narrated screen demo of the real `Pre Build Ideas/property-management/build` app — not generative video. The
credibility gate is satisfied the strongest way available: **every frame is the actual software
running**, driven like a real user, on the synthetic 220-unit portfolio, and the narration says so
out loud ("real, working software, running on synthetic data").

Structure (9 segments):
1. Title card (brand: indigo `#0F1226`, brass rule, lowercase `yourco`)
2. Resident app — home
3. Resident files the water-heater emergency start-to-finish (typing, urgency questions, entry
   notes, submit)
4. Manager board — the request already triaged P1, 0 minutes old
5. "Needs you" queue — why-a-human on every row; the deliberate absence of approve-all
6. Money — delinquency ladder, trust ledger; the never-moves-money line stated verbatim
7. Agents tab — the autonomy rungs, "earned on evidence, never assumed"
8. Owner view — counted, never asserted
5. **The vendor job card** (v4, 2026-08-17) — the plumber's magic-link work order: unit history
   with make/model/age, accept, window set, start, an after-photo uploaded, "Complete with
   proof — required" — the whole close, driven live
6. **The decline** — "Booked out this week" → the job moves to the next-ranked crew instantly,
   link closes on screen
6b. **Availability scheduling** (v5, 2026-08-17, three scenes) — a ROUTINE request (dripping
   faucet) filed with the intake availability chips (evenings, weekends, exact times; the VO
   notes emergencies skip the ask); the vendor card's "Resident can do:" one-tap pick confirming
   instantly, then a typed "Mon 7am sharp" becoming a proposal; the resident's "Does this time
   work?" card — "Works for me" books it. VO carries the staleness rule: a statement, never a
   standing pass to enter. Captured by `capture3.mjs` + `assemble5.sh`.
7. **The resident review** — "Yes, all good" opens the star picker; five stars swept, their own
   words typed, sent
8. **The vendor bench** — "What residents said": the fresh review at the top, verbatim
9. End card — "The AI does the work. People keep the judgment." + the honest-labeling line
   (original scenes 4–8 — Needs You, money, agents, owner — follow the new block unchanged)

## Pipeline (repeatable)
- **Capture:** `puppeteer-core` + system Chrome headless driving the live app (`capture.mjs`,
  scratchpad `posvideo/`) — injected brass cursor dot, real typing at 26ms/key, per-scene
  `page.screencast()` → webm. Mobile scenes at 2× page zoom for sharpness (390-CSS-px capture was
  soft at 1080p — found by QA frame). Store reseeded before the ordered run so the narrative is
  continuous (the request filed in scene 2 is the P1 on the board in scene 4).
- **VO:** Higgsfield `text2speech_v2` **ElevenLabs** variant, preset voice **Maeve**, 9 lines
  (v1 `seed_audio` read was flat — the Founder: "monotone robot" — lines rephrased conversationally; v2
  voice Maeve; v3 voice **Dylan** picked by the Founder from a 5-voice sample pass, **atempo 1.15** for
  pace, scene 2 video at 0.89× PTS so the submit still lands inside the tighter read;
  `assemble3.sh`). v4 adds four scenes captured by `capture2.mjs` (state pre-driven over the
  API so the filed request is the one dispatched, completed, and reviewed on screen; proof
  photo is a rendered stand-in image, everything else is the real app) + four Dylan lines,
  `assemble4.sh`.
- **Assembly:** ffmpeg — scenes freeze-padded (`tpad`) to narration length, mobile framed on the
  indigo canvas, cards faded, per-segment encode + concat. Script: `assemble.sh`.
- No music track (VO-only; clean educational read). Descript pass not needed at this length.

## Honesty & brand checks
- Every workflow shown exists and ran; no fabricated metrics — all numbers on screen are the
  synthetic seed's, and both cards + VO label the portfolio synthetic.
- White-label rules N/A (internal offering demo, yourco-branded on the cards only — the app
  surfaces carry the client-facing "Property OS" brand, no yourco mark inside the product).
- Wordmark lowercase (title card caught in caps by QA, fixed before ship).
- Agent names: none spoken or shown by name — "eight agents" by function only.

## Status
Internal / pre-gate. Nothing published; the file lives here and went to the Founder in-session.
Kolby's next weekly eval pass should include it (visuals shipped this week).
