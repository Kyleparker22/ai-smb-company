# Brand Audit Loop

> **Owner: Luka** (YourCo's Brand Custodian — see `agents/luka/`). Runs and signs as Luka. Flags + drafts only — guideline changes are in-loop with the Founder; never edits the guidelines autonomously. (Roster: monthly drift audit.)

## Cadence
First Monday of each month, AM (after the month's first loops have run). Plus on-demand whenever the Founder says "Luka, review X."

## Goal
Catch brand drift before it compounds. Scan what YourCo actually shipped last month against the locked brand guidelines, and flag anything off — so the brand stays coherent as more agents produce more surfaces.

## Inputs (read every run)
1. `brand/v0/brand-guidelines.md` — the locked standard (current version + the "Never use" lists)
- `brand/DESIGN.md` — the machine-readable spec (tokens · type · component idioms · hard rules). **Audit against this as well as the guidelines.** The guidelines catch voice and positioning drift; DESIGN.md catches a surface that violates §4's idioms or §7's hard rules while staying perfectly on-message. Added 2026-08-23 — before that this loop never read the design spec Luka owns.
2. Recent outputs since last audit: `loops/content/`, `loops/sales/`, `agents/reilly/copy-structure.md`, `agents/webb/pages/` (web), any new `decisions/` touching brand
3. Most recent prior artifact in `loops/brand-audit/` — for "what changed" and any open items
4. `brand/CHANGELOG.md`

## Steps
0. **Read recent learnings.** Before anything else, read the most recent entries (last ~5, past 30 days) in `/learnings/brand-voice/` for patterns that apply to this run, and apply what fits. List the entries you applied in the artifact's "Learnings applied this run" line. (An empty folder means nothing to apply yet — expected pre-launch.)
1. **Boot context.** Internalize the locked palette (indigo/cream/brass), typography rules (lowercase wordmark, tight display, 17px body, no italics-for-emphasis), voice "Never" list (no buzzwords: leverage/synergy/unlock/transform/revolutionize/10x/supercharge/cutting-edge; no hype emoji; no all-caps body), the Eval-Gate motif, the locked wordmark lockup, and the locked tagline ("We learn your business. AI does the work.").
2. **Scan outputs.** Check each recent surface for drift: off-palette color, banned words, wrong wordmark/tagline usage, italics-for-emphasis, pure white/black, gradients, drop-shadows-on-type, tone misses.
3. **Score + verdict.** Per surface: on-brand / minor-fix / rework. Note specific line + the rule it breaks.
3b. **Count the reviews.** Record how many assets were reviewed **before they shipped**, and how many cleared on the first review. *Pre-ship* means the asset was queued for review before it was published or sent — an asset you caught after it went out is a **Finding**, not a review. If nothing was queued, write **0**: that zero is the finding, because a brand custodian catching drift after ship has no first-pass rate to have.
4. **Drift watch.** Flag anything trending (a banned word recurring, a surface inventing its own style).
5. **Write artifact** at `loops/brand-audit/YYYY-MM-DD.md`.
6. **Slack summary** — 3 lines to `#yourco-luka`, signed "— Luka, YourCo Ops." Lead with anything that needs a fix before it ships externally.

## Output artifact format
```
# Brand Audit — YYYY-MM-DD

## Verdict
(Overall: clean / minor fixes / drift forming. One line.)

## Findings (surface → issue → rule broken → fix)
(Bullet per issue. "None" if clean.)

## Review volume
**N reviewed · M cleared first time** — pre-ship reviews only.

## Drift watch
(Patterns recurring across surfaces. Empty if none.)

## Guideline changes to propose to the Founder
(In-loop items — never applied autonomously. Empty if none.)

## What I'd do differently next run
(Empty — for the Founder to fill)

## What worked this run
(1-2 things that landed harder than expected. Future runs read this too — this is how wins get amplified, not just mistakes avoided.)

## Learnings applied this run
(The `/learnings/brand-voice/` entries that influenced this run. "None" if nothing applied.)
```

> ⚠️ **`## Review volume` is machine-read.** `dashboard/loop_metrics.py` parses that heading and the
> `**N reviewed · M cleared first time**` line to produce Luka's owned number on HQ → Agents
> (`runtime/agent-registry.json` → `agent_metrics`). Keep the heading text and the shape exactly;
> rename either and the metric reports a parse failure — which is the designed behaviour, and still
> means the number disappears until someone fixes it.

## Watchdog triggers
- Same drift flagged 2 audits running, unfixed → escalate at the top.
- Any banned word or off-palette color on a customer-facing surface → flag as fix-before-ship.
- A surface inventing its own design language (not in guidelines) → flag.

## Pre-scale handling
Few surfaces today; the audit is short and honest. As agents multiply, it grows. The point is to never let drift become the norm.
