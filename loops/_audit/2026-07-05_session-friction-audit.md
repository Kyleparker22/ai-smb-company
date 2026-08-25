> ⚠️ **EXAMPLE — not yours.** From the source company; restored because other pages cite it.

# Session friction audit — 2026-07-05

First-ever audit of the Founder's own Claude Code sessions (42 transcripts, 2026-06-09 → 2026-07-05, ~1,100 user messages) hunting where the Founder's time gets wasted: re-explained context, corrections, repeated procedures, permission friction, abandoned threads. Method: transcripts digested to user-messages + denials + tool errors, five parallel analysts over non-overlapping slices, one completeness critic cross-checking (which also reconciled findings against the repo so already-fixed items don't get re-recommended). Companion to the 2026-07-04 full OS audit (which was ops/business-level; this is workflow-level).

**Headline: the #1 sink is the Founder acting as a human SSH relay to the VPS (~85+ messages across 5 sessions). #2 is the "what are your thoughts on X for yourco?" triage being re-derived from scratch 25+ times. #3 is credential onboarding as ad-hoc Q&A (~18 rounds, 14 services). Most standing-constraint violations trace to rules that lived only in the Founder's head until broken.**

---

## Confirmed clusters (multiple analysts, independent slices), ranked by cost

### 1. The VPS human-relay (~85+ messages; 4 of 5 analysts) — OPEN
Every runtime deploy/debug: Claude writes commands → the Founder SSHes in → pastes them → pastes raw output back ("how do i exit nano in the terminal", "which server do i paste these in", one paste ran VPS commands on the Mac by mistake). The systemd install ritual alone was hand-run 7+ times. When Claude tried to SSH itself, the auto-mode classifier denied it — the VPS coordinates aren't in boot context, so the IP looked invented.
**Partially fixed:** `runtime/phone-access.md` now carries the SSH command *for the Founder*. The open half is Claude-facing:
- (a) CLAUDE.md pointer: host `user@your-vps` (Tailscale), repo `~/yourco-os` → *applied in this audit's CLAUDE.md patch*
- (b) allowlist a scoped `ssh user@your-vps …` pattern in settings (diagnostics + the unit-install one-liner; deny stays for destructive ops)
- (c) **VPS self-deploy** — the real fix: a sudoers-scoped script/timer on the VPS that git-pulls, diffs `runtime/systemd/`, installs changed units, daemon-reloads, enables, posts result to Slack. Adding a loop should never need human hands. (Owner: Kemba/platform. Proposed by 3 analysts independently.)

### 2. Tool/repo triage re-derived every time (25+ occurrences, 3 analysts) — skill created
"What are your thoughts on X for yourco?" is the single most common interactive kickoff (AIOS, Attio, Twenty, Runner, agency-agents, 50-item lists…). `decisions/2026-07-05_tool-triage.md` created the *filter*; the *procedure* wasn't a skill, so each session re-derives it (one even researched the wrong product). → **`.claude/skills/tool-triage/` created in this audit**: identify → verify → moat-fit score → adopt / steal-pattern / trigger-gate / skip → dated artifact + decision log → brief affected agents → never pull focus from the beachhead.

### 3. Credential onboarding is ad-hoc Q&A every time (~18 rounds, 14+ services, 2 analysts) — skill created
Slack (missing_scope ×3), Instantly (wrong scope), Outscraper, YouTube, Bluesky, Yelp, Twilio, Pexels, xWeather, Visual Crossing, HailTrace, Firecrawl… same loop: "where do i enter the key? what scope?" then a wrong-scope debug round. Downstream cost: Sadie's loop shipped with dead YouTube/Bluesky sources because keys never landed. → **`.claude/skills/wire-credentialed-connector/` created in this audit**: exact env file + machine up front, console click-path with required scopes, echo-append not nano, live verify call, register in `runtime/connectors.md`. Complements `deploy-vps-daemon`.

### 4. Silent failures — nothing watches the watchers (3 incidents, 3 analysts) — PARTIALLY OPEN
Runtime dead ~3 days on credit exhaustion (noticed late); brett-ideas first run failed silently; Slack control surface dead all weekend ("total silence" — private channels + missing mappings), found only when the Founder tried to use it mobile. The credit alarm is built (`runtime-alarm.sh` + auto-reload). **Open:** a listener/control-surface heartbeat — verify `yourco-slack-listener` alive, every rostered agent has a mapping, atlas is member of each channel; plus a FAILED-exit check on loop logs. Right-sized: fold into the Mon 07:45 governance watchdog (or daily).
*Related, shipped today: the dashboard now derives loop health from the repo (`dashboard/refresh.py`) — it immediately surfaced that `melanie-briefing` has never committed an artifact despite its prompt requiring one, plus the known never-wired brand-audit/pricing-review/open-loops-chaser.*

### 5. Broken localhost links (~22 wasted messages, 2 sessions) — CLAUDE.md line applied
Claude invented server names ("yourco-site", "yourco", "yourco-dashboard", "nick-storm-demo") instead of reading `.claude/launch.json`; "none of those are working" was sent 11 consecutive times. Deterministic failure, trivial fix, highest value-per-effort in the set. → *CLAUDE.md line applied: launch.json is the only source of server names; new demos get an entry + a verified-responding URL before sharing.*

### 6. Standing constraints learned by violation (5 rules, 3 analysts) — CLAUDE.md block applied
Each rule cost a correction round + rework before it was written down: don't-deploy-until-OtherVenture (restated 5+ times, now gated properly); **OtherVenture/yourco hard separation** (scrubbed 3 times: site copy, email, git identity); **agent names internal-only** on external surfaces; **no specific prices** on the public site; **white-label client-facing apps** (Sample Product shipped with yourco branding by default); stats must be recent. → *merged into one "External-surface rules" block in CLAUDE.md.*

### 7. The premium design bar exists only reactively (12 rounds on the Reed video, 17 on the home hero) — CLAUDE.md line applied
Same verbatim quote in two different media a week apart: "looks like I spent $5/$500 on it and I want it to look like $50,000." → *one line in the CLAUDE.md brand pointer: the $50k bar + present 2–3 options before iterating live on hero-grade visuals.*

### 8. Abandoned threads with no resume artifact (4 analysts) — route to Jim
Flagship: the Google Alerts intent engine — ~40 messages of manual setup, zero signal in 2 weeks, then the funnel was parked; disposition of the ~10 configured feeds never decided. Also: QuickBooks OAuth 403 (chosen twice, never landed), Twilio RCS verification (a 4–6-week clock, stalled), Recraft/Vapi/Nano-Banana "later" items, Sample Product "Where to Knock feeds not populating" bug + the route-planner request (last message before context exhaustion — completion unverified). The *mechanism* now exists (Jim's weekday open-loops chaser, first run Mon 07-06). → **Seed these specific items into Jim's first ledger** rather than assuming he'll find them; the meta-lesson for `learnings/`: a channel buildout gets a validation checkpoint *before* 40 messages of manual labor, not after.

### 9. Two-writer git topology conflicts (1 analyst, but 5 documented failures — treat as strong) — OPEN
The Mac's daily `yourco-os-git-backup` scheduled task and the VPS runtime both push to main: "fetch first" rejections, an add/add conflict on a same-day `loops/` artifact, a detached-HEAD commit, and one blocked `git reset --hard` recovery attempt. `processes/git-sync.sh` has no pull-before-push. **Fix:** pull `--rebase` + retry-once in git-sync.sh, never destructive recovery; or retire the Mac backup and let the VPS own pushes (Mac pulls only). → *sync-model line added to CLAUDE.md; script fix queued with the bug-hunt fixes.*

### 10. Secrets pasted into chat (critic-surfaced; no analyst flagged it) — FOUNDER ACTION
API keys, client IDs, and secrets were pasted directly into chat repeatedly (xWeather, Slack, Instantly, Twilio…) — those now live in stored session transcripts on disk. **Recommend: rotate the keys that were pasted, and adopt the convention that secrets go straight into the (gitignored) env file, never into chat** — the wire-credentialed-connector skill encodes this. This is the most serious single item in the audit.

## Demoted (looked like patterns, aren't)
Duplicate back-to-back sends (client latency symptom, not behavior); "File has not been read yet" tool errors (harness-level, self-correcting); the add-intent-vertical skill idea (codifies a dead procedure — funnel parked 06-22); "the Founder always says do-whatever-you-recommend" as a CLAUDE.md rule (thin evidence; the autonomy matrix already owns this); a standalone credit-balance alarm (already built).

## Next-audit lenses (the critic's gaps — scope for the recurring run)
Loop-artifact consumption (are the 20 loops' outputs read or write-only noise — does Step 0 actually fire?), skill-adoption efficacy (do sessions invoke the 11 skills or re-derive?), permission-prompt sweep (a fewer-permission-prompts pass), session-time vs commercial priorities (the 07-04 audit's point: enormous effort on triage/polish while Sample Client sat at Proposal), token/context cost of the relay patterns.

## Recommend
Make this a monthly loop (Kolby-shaped, ~1st Sunday): digest new transcripts → cluster → diff against this artifact → propose. The digest script is reusable: this session's scratchpad `digest_sessions.py` — worth carrying into `runtime/` if the loop is adopted.
