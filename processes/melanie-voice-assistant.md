# Melanie — the dashboard voice assistant

> Melanie is yourco's HQ dashboard assistant (the "JARVIS" — named for **Melanie Smooter**, the CEO-in-training agent, with a warm Southern Alabama voice). You ask a question (type or speak), she answers from the company's real data, and speaks the answer back. Lives in `dashboard/index.html` (the floating console, bottom-right). **Internal tool — runs locally, no external surface.**

## The requirement (the Founder)
"Only do the voice thing if I ask Melanie a question and she gives me answers." → so Melanie must be a real **Q&A assistant**, not a script-reader.

## Phase 1 — LIVE NOW (free, no keys)
- **Ask:** type in the console, or click the mic (browser `SpeechRecognition` → speech-to-text; Chrome).
- **Answer:** `askMelanie()` matches the question to intents and answers from the **live dashboard data** (`D.pipeline`, `D.agents`, `D.company.focus`, `D.company.metrics`, `D.loops`). She handles: leads / pipeline value, who's live, the team size, this week's focus, loops, clients/MRR/runway, compliance status, overall status. Grounded — never made up.
- **Speak:** browser `speechSynthesis` reads the answer (a generic US female system voice — **not** a real Southern accent yet).
- Southern personality is in the text ("sugar," "hon," "runnin' just fine").

## Phase 2 — the real voice + open-ended brain (BUILT — staged, switch-flip on keys)
**The backend is built and wired.** `dashboard/melanie.py` (the brain + voice) + `/api/melanie` on `dashboard/server.py`; the console (`dashboard/index.html`) now POSTs to it and falls back to Phase 1 when keys are absent. It runs the moment the Founder drops in the keys — **no code change, no `pip install`** (stdlib-only; prefers the `anthropic` SDK if it happens to be installed). The two upgrades, both via the local endpoint (keys can't live in the client-side dashboard):
1. **Open-ended brain → Claude API.** Swap `askMelanie()`'s intent-matching for a call to a backend `/api/melanie` that sends the question + the assembled company context (CRM, dashboard data, key docs) to **Claude** and returns the answer. Then she can answer anything, not just the pre-built intents.
2. **The real Southern Alabama voice → ElevenLabs.** The backend calls ElevenLabs TTS with a Southern-American female voice and returns the audio; the console plays it instead of browser TTS.
   - **Voice Design prompt:** *"A warm, friendly Southern American woman in her late 20s with a gentle Alabama drawl — relaxed, charming, conversational, a little playful."*
   - ⚠️ **Do not clone Reese Witherspoon's voice** (likeness/IP). Design a generic Southern voice that evokes the Melanie Smooter vibe.

### What the Founder provides to flip it on (the only thing left)
1. `cp dashboard/melanie.env.example dashboard/melanie.env` and fill in:
   - `ANTHROPIC_API_KEY` — the Claude brain (console.anthropic.com).
   - `ELEVENLABS_API_KEY` + `MELANIE_VOICE_ID` — fund ElevenLabs (balance was $0), design the Southern voice (prompt below; **do NOT clone Reese Witherspoon**), paste the voice id.
   (Or set them as real env vars before starting the server.) `melanie.env` is gitignored — keys stay server-side, never the browser.
2. Restart the dashboard so it picks up the keys: `./show.sh stop && ./show.sh` (a server already running on :8791 keeps the old code until restarted).
   - Verify: `curl -s localhost:8791/api/melanie` → `{"brain":true,"voice":true,...}`.

### What's built (done)
- `dashboard/melanie.py` — `assemble_context()` (live dashboard + CRM + an "about yourco" blurb), `ask()` → Claude (`claude-opus-5`, SDK-if-present else raw HTTPS), `speak()` → ElevenLabs mp3 (base64 data URL), `answer()` with a 5-min cache + 30/min rate limit. Graceful: no/blank key or a failed call → `backend:"unconfigured"` so the browser falls back.
- `dashboard/server.py` — `POST /api/melanie` (the answer) + `GET /api/melanie` (a `{brain,voice}` status probe), same-origin on :8791.
- `dashboard/index.html` — `melAsk()` POSTs to `/api/melanie`; on `backend:"live"` it renders Claude's text and plays the ElevenLabs audio; otherwise it falls back to the Phase-1 grounded answer + browser speech. Phase-1 `askMelanie()`/`speak()` kept intact as the fallback.
- `dashboard/melanie.env.example` (template) + `.gitignore` entry for `melanie.env`.

### Voice Design prompt (for ElevenLabs)
*"A warm, friendly Southern American woman in her late 20s with a gentle Alabama drawl — relaxed, charming, conversational, a little playful."* ⚠️ **Do not clone Reese Witherspoon's voice** (likeness/IP) — design a generic Southern voice that evokes the Melanie Smooter vibe.

## Honest status
Phase 1 works today and meets the bar (ask → real answer → spoken). Phase 2 (answer-anything Claude brain + real Southern ElevenLabs voice) is **built and wired** — it sits dormant behind the keys and turns on the moment the Founder adds them and restarts. Verified locally: with no keys the endpoint returns `unconfigured` and the console falls back cleanly; the rest is the Founder's funded keys.
