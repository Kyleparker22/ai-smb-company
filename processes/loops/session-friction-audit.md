# SOP — session-friction-audit (monthly)

**Cadence:** monthly, 1st Sunday ~18:00 ET. **Owner:** Kolby (QA/eval-shaped — this is eval applied to the Founder's own tooling). **Runs:** Mac-local (via the scheduled-tasks MCP, `taskId: session-friction-audit`), **not** the VPS runtime — see "Why Mac-local" below.

## Purpose
Audit the Founder's recent Claude Code sessions for **friction** — where his time/attention was wasted, where he re-explained context, corrected the model, hit permission prompts, or asked for the same multi-step thing again — and emit concrete fixes: new skills, CLAUDE.md/memory edits, automation candidates, and abandoned-thread follow-ups. This is the closed-loop discipline (observe → write → next run adjusts) pointed at the tooling itself, and it dogfoods the eval-and-improve story yourco sells.

## Why Mac-local (not a VPS systemd loop)
The valuable transcripts are the Founder's **interactive** sessions, which live on his Mac at `~/.claude/projects/<project-key>/`. The VPS runtime only has its own headless-loop transcripts. So this loop must run where the Founder's sessions are. It is therefore **not** in `runtime/agent-registry.json`'s sanctioned VPS timers (adding it there would trip the governance watchdog as false drift) and **not** in `runtime/run-loop.sh`. It rides the `scheduled-tasks` MCP instead, which runs a self-contained Claude Code task locally when the Cowork app is open (missed runs fire on next launch).

## Secrets rule (load-bearing)
Digests can contain API keys/secrets the Founder has pasted into chat. `runtime/session-digest.py` writes them to **`~/.yourco/session-digests/`** — outside the repo entirely — and the run **deletes them when done**. Digests are NEVER committed. (This is the same class of exposure the 2026-07-05 audit itself flagged.)

**Why outside the repo, not just gitignored (changed 2026-08-02):** this Mac has iCloud "Desktop & Documents Folders" sync ON, so `~/Documents/…/yourco` — including every gitignored path in it — uploads to iCloud. Gitignore is a *commit* boundary, not a privacy boundary. Two consequences this loop hit directly: secrets-bearing digests were syncing to iCloud, and re-running the digest script mid-audit left 75 ` 2.md` conflict copies that would have doubled every occurrence count. If you ever see ` 2.md` files in a digest dir, dedupe before counting. See `learnings/ops/2026-08-02_synced-workspace-is-not-a-privacy-boundary.md`.

## Method (each run)
0. **Step 0 (loop contract):** read the last ~5 `learnings/ops/` entries and the prior audit artifact `loops/_audit/*_session-friction-audit.md`; apply what fits, and list it under "Learnings applied this run." Scan `.claude/skills/` before proposing a skill (don't re-propose an existing one).
1. **Digest:** `python3 runtime/session-digest.py --since 35` → per-session digests in the gitignored dir. Read the printed table to see the corpus.
2. **Cluster:** analyze the digests for friction. For a large corpus (≥~15 sessions) fan out subagents over slices (one per big session + one for the small-session tail) and cross-check; for a small corpus a single pass is fine. Every finding needs a verbatim quote + session id; **count occurrences honestly — one-offs are not friction.**
3. **Reconcile against the repo** before recommending: several fixes may already have shipped (check `decisions/`, `.claude/skills/`, `runtime/`, CLAUDE.md). Don't re-recommend done work — that dilutes trust in the open items.
4. **Diff against the prior audit:** what recurred, what's newly resolved, what's still open.
5. **Emit fixes**, each mapped to a surface: new **skill** (`.claude/skills/`), **CLAUDE.md/memory** edit for repeated context, **automation/loop** candidate, or **abandoned-thread** item → seed `loops/open-loops/` for Jim.
6. **Cleanup:** delete `loops/_runtime/session-digests/`.

## Output (done-state)
- `loops/_audit/YYYY-MM-DD_session-friction-audit.md` — headline (top sinks), confirmed clusters ranked by cost with evidence, what shipped this run vs what's queued for the Founder, and next-run lenses.
- Any skills/learnings/CLAUDE.md edits actually made this run (list them in the artifact).
- Commit the artifact + any edits (NOT the digests). No Slack post required; if posting, lead with the top-1 fix.

## Empty / quiet handling
If < ~3 sessions since the last run, say so and stop — "quiet month, N sessions, nothing clustered" satisfies the contract. Never manufacture findings.

## Failure modes
- No transcript dir (fresh machine / different path) → `session-digest.py` exits 1 with a clear message; report "no local sessions to audit."
- Corpus too large for one context → fan out (step 2); never truncate silently — say what wasn't read.
