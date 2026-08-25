---
name: tool-triage
description: Evaluate an external tool, repo, video, newsletter, pattern — or a piece of content (article, essay, podcast transcript, book, an operator's philosophy) — for yourco adoption. Use whenever the Founder asks "what are your thoughts on X?" / "should we add this?" / "anything to take away from this?" / pastes a link, listicle, transcript, or article for review — the most common interactive kickoff by a wide margin (25+ in June–July 2026; 13 more in the four weeks to 2026-08-02, about half of them content rather than tools), previously re-derived from scratch every session.
---

# tool-triage — evaluate an external thing for yourco

## When
Any "should yourco adopt/consider/steal X?" request — a GitHub repo, SaaS product, YouTube transcript, newsletter pattern, agent framework, or loop idea. NOT for client-engagement tooling choices (those are delivery decisions) or for things already triaged — check step 1.

**Two input shapes, one procedure.** *Tool-shaped* (repo, product, framework, API) runs the full step list below. *Content-shaped* (article, essay, podcast/video transcript, book, an operator's playbook — Cuban, Portnoy, Sabri Suby, the Constellation "invisible companies" essay, the Anthropic context-engineering post) skips step 3's repo checks and instead: name the **one transferable mechanism** in a sentence, decide whether yourco already does it, and route it. Content triage still ends at step 6 — the tell that it wasn't logged is the Founder typing "okay log this" / "say the word — log it all" after the analysis, which happened repeatedly in July. Do step 6 without being asked.

## Steps
1. **Check prior art first.** Grep `decisions/` (especially `decisions/2026-07-05_tool-triage.md` — the standing filter + past verdicts) and `loops/` triage artifacts. If X was already triaged, restate the verdict and only re-open if something material changed.
2. **Positively identify X.** the Founder's links/names are often ambiguous ("Runner" once resolved to the wrong product and needed a second research pass). Confirm the exact product/repo before evaluating; use WebSearch/WebFetch — never evaluate from name recognition alone.
3. **Verify the claims.** Read the actual repo/docs, not the marketing. For repos: stars ≠ quality; check recency, license, and whether it actually does what the pitch says.
4. **Score against the locks and the moat.** Stack locks (Vapi for voice, Higgsfield for video, etc. — see CLAUDE.md + `decisions/`), the moat filter (does it strengthen reliability/eval/observability/approval, or is it commoditized tooling?), compliance posture (ToS-violating scrapers = auto-SKIP), and current priorities (Sample Client, runway, launch gate).
5. **Issue one of four verdicts:** **adopt** (rare — say what, where, who owns it) · **steal the pattern** (name the specific pattern and which agent/doc absorbs it) · **trigger-gate** (good later; write the activation trigger into `runtime/activation-triggers.md` or the relevant doc) · **skip** (one honest sentence why).
6. **Log it.** Update `decisions/2026-07-05_tool-triage.md` (or a dated triage artifact for big batches), and brief the specific affected agents' docs if the verdict changes how they work.
7. **Guard the beachhead.** If evaluating or adopting X would pull focus from the current commercial priority, say so explicitly in the verdict — that's part of the answer, not a footnote.

## Gotchas
- The wrong-product misidentification (step 2) has actually happened — don't skip it.
- Don't let a 50-item list turn into 50 deep dives; batch-triage with one-line verdicts and deep-dive only the adopt/steal candidates.
- A verdict that isn't logged will be re-asked — step 6 is what makes the skill compound.

## Canonical doc
`decisions/2026-07-05_tool-triage.md` holds the filter criteria and the verdict ledger; this skill is the procedure around it.
