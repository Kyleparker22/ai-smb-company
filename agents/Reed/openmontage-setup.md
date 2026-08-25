# OpenMontage — setup guide (Reed's real-footage video engine)

> **⛔ DEPRECATED 2026-06-23 — OpenMontage dropped from the pipeline** (`decisions/2026-06-23_Reed-higgsfield-not-openmontage.md`). Reed now uses **Higgsfield** (sole engine) + **Descript** (assembly/VO/overlays). This doc is kept for history only; do not follow it as the current standard. The paired Slack bridge (`runtime/montage_slack_bridge.py`) is also deprecated.

> The agentic, real-footage video system adopted 2026-06-17 (`decisions/2026-06-17_Reed-realistic-video-openmontage.md`).
> Repo: https://github.com/calesthio/OpenMontage (open-source, AGPLv3, ~March 2026, fast-moving/new). It turns Claude
> Code into a video studio — research → script → assets → edit → compose, with human-approval gates on creative stages.

## One-liner
the Founder clones one repo and runs `make setup` on his Mac (needs Python 3.10+, Node 18+, FFmpeg first). **Zero API keys
required** for real-footage video (Archive.org/NASA/Wikimedia + offline Piper narration work out of the box). After
that, **Reed drives it entirely in plain English inside Claude Code.**

## Where it runs
**the Founder's local machine (Cowork/local Claude Code) — NOT the headless VPS.** It reads repo files and calls Python
tools via shell, and the runtime gate denies Bash. So OpenMontage is a Cowork/local tool: the Founder sets it up; Reed
operates it conversationally in a Claude Code session; output (the MP4) gets human-approved before any external use
(the reframed credibility gate).

## Prerequisites — the Founder installs (one-time)
- **Python 3.10+**, **Node.js 18+**, **FFmpeg**. On Mac: `brew install ffmpeg node python`.
- Claude Code (already have it). macOS supported (the Founder's on Darwin).
- Disk: unspecified by the repo — assume several GB (rendered MP4s + footage cache under `projects/`).

## Install — the Founder runs (exact, from the README)
```bash
git clone https://github.com/calesthio/OpenMontage.git
cd OpenMontage
make setup
# manual equivalent if `make` is unavailable:
# pip install -r requirements.txt && cd remotion-composer && npm install && cd .. && pip install piper-tts && cp .env.example .env
make test-contracts   # sanity check, works with no keys
```
Integration is via the repo's root instruction files — `CLAUDE.md` points the agent to `AGENT_GUIDE.md`. No MCP
server or plugin to register; you just open the OpenMontage folder as the project in Claude Code.

## API keys — all optional (the Founder's call; go in `.env`)
- **Free, no key:** Archive.org, NASA, Wikimedia (real footage); Piper TTS (offline narration); Remotion + FFmpeg.
- **Free key, recommended for better stock coverage:** `PEXELS_API_KEY`, `PIXABAY_API_KEY`, `UNSPLASH_ACCESS_KEY`.
- **Paid, optional (likely NOT needed for real-footage demos):** `FAL_KEY`, `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`,
  `GOOGLE_API_KEY`, etc. — only for generated assets/premium voices.
- **No separate Anthropic key** — Claude Code is the driver (uses existing Claude Code auth).

## How Reed runs a job (fully conversational)
Open the OpenMontage folder in Claude Code and brief it in plain English, e.g.:
- *"Make a 90-second documentary montage about what running a hardscaping business feels like. Real footage only, no narration, confident tone."*
- For yourco's realistic demos, steer to the **`hybrid`** pipeline (the production-grade, footage-led one); phrasing
  like "use real footage only" routes there. Output: `projects/<name>/renders/final.mp4`.

## Fits the credibility gate
OpenMontage **forbids silent runtime swaps / substituting animation when motion footage was specified** — which
aligns with yourco's reframed rule: no AI/stock footage passed off as real captured client work; every demo
represents what yourco will actually build + deliver; Kolby evals + the Founder approves before any external use.

## Caveats
- **AGPLv3** — fine for making yourco's own marketing/demo videos; **do not fold its code into a hosted yourco
  product** without legal review (copyleft bites on distribution / network-service use).
- New + fast-moving repo; several footage pipelines are **beta** (`hybrid` is the production one). Local GPU
  video-gen is experimental — skip for v1.

## Control it from Slack (optional — `runtime/montage_slack_bridge.py`)
You can fire briefs from Slack and get the rendered video back, mirroring yourco's existing Slack control surface.
**It runs on your Mac** (OpenMontage is local; the VPS can't), so **your Mac must be awake/online** when you use it.
- **Flow:** post a brief in the Montage channel → bridge acks → runs Claude Code headless in the OpenMontage repo
  (venv on PATH) → finds the newest `final.mp4` → **uploads it to the channel for your review.** It never publishes
  anywhere external — you decide what ships (the credibility gate stays human).
- **Setup (one-time):** (1) in Slack, create a channel — default `#yourco-Reed` (or set `MONTAGE_SLACK_CHANNEL`)
  and invite the yourco bot; (2) `pip install slack_sdk` inside the OpenMontage venv; (3) put `SLACK_BOT_TOKEN`,
  `SLACK_APP_TOKEN`, `FOUNDER_SLACK_USER_ID` in `runtime/.slack.env` (same app as the agent listener) and set
  `OPENMONTAGE_DIR=~/Documents/OpenMontage`; (4) run it on the Mac with the venv active:
  `python3 runtime/montage_slack_bridge.py` (or `--self-check` first). Hardened like the agent listener:
  **the Founder-only, rate-limited, your message is the only instruction.** Renders take minutes → it's async.

## Owner split
**the Founder:** one-time install (FFmpeg/Node/Python, clone, `make setup`, any free/paid keys in `.env`).
**Reed:** everything after — briefing, pipeline choice, asset gen, edit, render, iterate — conversationally.
