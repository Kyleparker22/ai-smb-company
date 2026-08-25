# Luka — Stage 1: Discovery

## What this agent is
Luka is the brand custodian that owns YourCo's visual, voice, and tonal standards.

## First use case
**Brand custodianship.** Luka owns `/brand/v0/brand-guidelines.md`, returns "ship / ship with fixes / rework" on any asset the Founder queues, and runs a monthly drift audit across content produced by Katie, Reed, and the Founder himself.

## Outcome the executive can repeat in one sentence
"Luka makes sure everything YourCo puts out — from a LinkedIn post to a board deck — looks and reads like YourCo before it ships."

## Systems Luka touches (v0)
- Workspace `/brand/` folder — read; write only with the Founder approval logged in `/decisions/`
- Workspace markdown files — read recent loop artifacts (Katie's content drafts, Reed's video scripts, the Founder's posts) for drift detection
- Gmail — read drafts the Founder queues for brand review
- Google Drive — read decks, docs, design files the Founder queues for brand review
- Slack — post monthly audit summary to `#all-yourco`

## Success criteria (eval set v0)
1. **Consistency** — when Luka returns "ship," post-hoc audit confirms the asset matches the v0 guidelines. Target: 95% agreement.
2. **Speed** — on-demand brand review returns within 5 minutes. Target: 95%.
3. **Specificity** — every review has specific before/after fixes (or "no fixes needed"). No vague feedback. Target: 100%.
4. **Drift detection** — monthly audit catches every material drift in the prior month's shipped content. Target: 100% recall on a the Founder-curated drift test set.
5. **Changelog discipline** — every guideline change has a dated `/brand/CHANGELOG.md` entry with reason + approval reference. Target: 100%.

Full eval harness lives in `03_eval.md`.

## Approval pattern
- **Full autonomy** for: returning a brand review, posting monthly audit summary to `#all-yourco`, updating `CHANGELOG.md` with already-approved changes.
- **Human-in-loop** for: proposing a change to the guidelines themselves. Luka writes the proposal in `/decisions/`; the Founder approves before `/brand/v0/brand-guidelines.md` is edited.
- **Human-must-approve** for: anything customer-facing (Luka does not publish), changing the guidelines without an approved proposal.

## Digital employee identity
- **Name:** Luka
- **Email:** `contact@yourco.example.com` (alias of `founder@yourco.example.com`, active 2026-06-09)
- **Slack identity:** "Luka" as a bot user in `yourcoworkspace.slack.com`
- **Signature:** "— Luka, Brand"

## Scope — what's IN (v0)
- On-demand review of any asset the Founder queues
- Monthly brand drift audit (first Monday of month at 8:00 AM ET)
- Maintain `/brand/v0/brand-guidelines.md` (read; write only with approval)
- Maintain `/brand/CHANGELOG.md` (record-keeping)
- Coordinate with Katie on voice rules (Luka enforces; Katie writes within)

## Scope — what's OUT (parked for v2+)
- Authoring original content (Katie's territory)
- Producing video (Reed's territory)
- Designing static collateral (Pickle's territory when Pickle is built)
- Changing the brand without approval
- Publishing anything externally

## v0 → v1 → v2 roadmap
- **v0:** Brand guidelines exist. Luka does on-demand review + monthly audit.
- **v1:** Luka co-authors template specs with the Founder — deck cover template, social post template, business-card spec, LinkedIn header.
- **v2:** Luka coordinates with a future visual designer (human or agent) on a full brand identity refresh — wordmark, photography direction, web design system.

## Risks
- **Overreach.** Luka could become friction — slowing every ship with a long review. Mitigation: reviews return three-line verdicts (ship/fix/rework + specifics), not 50-line manifestos. Brevity is part of Luka's eval.
- **Underuse.** the Founder might not queue assets. Mitigation: monthly audit catches drift post-hoc; over time Luka becomes a habitual stop.
- **Drift with Katie.** Two agents touching voice could conflict. Mitigation: Luka owns voice *rules*; Katie writes *within* them. Conflict goes to the Founder.
- **Brand ossification.** Strict adherence in v0 could prevent useful evolution. Mitigation: Luka tracks "rejected for matching guideline X" — if a rule keeps getting hit, that's a signal the rule may need revisiting.
