---
name: synced-workspace-is-not-a-privacy-boundary
description: The yourco workspace lives in iCloud-synced ~/Documents, so gitignore stops commits but not uploads — every runtime/*.env secret is in iCloud, and rapid rewrites leave " 2" conflict copies that corrupt any file-counting analysis.
metadata:
  type: feedback
---

Found 2026-08-02 during the monthly session-friction audit. Two facts, verified on the box:

1. **`~/Documents` is the iCloud container.** `stat` on `CLAUDE.md` returns the *same inode* for `~/Documents/Claude/Projects/YourCo LLC - AI/CLAUDE.md` and `~/Library/Mobile Documents/com~apple~CloudDocs/Documents/Claude/Projects/YourCo LLC - AI/CLAUDE.md` — macOS "Desktop & Documents Folders" sync is ON. The whole workspace continuously uploads to iCloud, and that includes every gitignored path: `runtime/.slack.env`, `.twilio.env`, `.instantly.env`, `.anthropic-admin.env`, `.firecrawl.env`, `.outscraper.env`, `.recraft.env`, `.yelp.env`, `.bluesky.env`, `.youtube.env`, `dashboard/melanie.env`, and the session digests this very loop writes.
2. **Rapid rewrites produce conflict copies.** Running `runtime/session-digest.py` twice in a few minutes left **75 ` 2.md` duplicates** alongside 153 real digests — the script deletes and rewrites its output dir, and the sync daemon resurrects the in-flight copies under the classic macOS " 2" name. The audit's own grep counts were silently ~2× inflated until the duplicates were spotted.

**Why:** the OS's secrets discipline (`.claude/skills/wire-credentialed-connector/`, the "secrets never get pasted into chat" rule) treats **gitignore** as the containment boundary. Gitignore governs what enters the *repo*, nothing more. On a synced Mac the real boundary is the filesystem path, and every credential yourco holds is currently on the wrong side of it. This is the same shape as the pasted-secrets exposure the 2026-07-05 audit flagged: the secret is safe from the place we were watching and sitting in the place we weren't. Second-order: any analysis that *counts files* inside a synced tree is unreliable without deduping, which quietly attacks the honesty of file-based audits.

**How to apply:**
1. **New credentials go to `~/.yourco/`, not `runtime/*.env`.** Precedent already exists (`~/.yourco/reddit.env`). `wire-credentialed-connector` should default there for any new key; migrating the ten existing env files is a the Founder decision (queued in the 2026-08-02 audit), not something a loop should do unattended — moving a key that a running daemon reads breaks the daemon.
2. **Nothing secret-bearing gets written inside the repo, gitignored or not.** `session-digest.py` now defaults to `~/.yourco/session-digests` for exactly this reason.
3. **Dedupe before counting.** Any run that tallies occurrences across files in `~/Documents` must exclude `* 2.*` conflict copies first, and should not re-run a generator mid-analysis.
4. **Don't extend the inference.** iCloud sync is not a breach; it is Apple-encrypted storage tied to the Founder's account. The point is that the boundary we *documented* and the boundary that *exists* are different, and only one of them is in the threat model. Related: [[2026-07-06_cross-session-drift]].

Audience: Atlas/platform (ops) · Kolby (this loop's owner) · anyone invoking `wire-credentialed-connector` or writing gitignored artifacts.

Triggers: skill:wire-credentialed-connector, agent:rafi, gitignored artifact, secret handling, privacy boundary, synced repo