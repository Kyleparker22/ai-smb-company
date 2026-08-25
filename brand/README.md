# /brand/

YourCo's brand system. Owned by Luka (see `agents/luka/`). Source of truth for everything YourCo ships externally — visually and verbally.

## Files
- `v0/brand-guidelines.md` — current guidelines (v0, June 2026) — the narrative system (the *why*)
- `DESIGN.md` — **the machine-readable design spec** (tokens, type, component idioms, hard rules) — the visual twin of `writing-rules.md`. Loaded by the `brand-audit` (Luka) and `content` (Katie) prompts and the `visual-brand-qa` skill. *(Until 2026-08-23 it declared this loading contract in its own §8 and **nothing honoured it** — not even Luka's own monthly audit, which read only the guidelines. A surface could break every idiom in §4 and pass. Now invariant-checked.)*
- `writing-rules.md` — the sentence-craft constraint block. Loaded at Step 0 by the `content` (Katie), `outreach-eval` (Kolby), `aeo-geo` (Mario) and `deal-agent` (David) prompts. *(This line used to read "Katie/Reilly/Melanie" — corrected 2026-08-23: Reilly has no loop prompts at all, and neither of Melanie's loads it. Coverage was fine; the description was wrong.)*
- `LOGO.md` + `yourco-*.png` — logo files and where each is used
- `CHANGELOG.md` — every change, with reason and the Founder's approval reference

## How to use this
Before shipping any external asset (LinkedIn post, deck, one-pager, demo, email), queue it for Luka with: "Luka, review this." Luka returns one of three statuses:
- **ship** — no fixes needed
- **ship with fixes** — small specific changes; usually <5 minutes to apply
- **rework** — material drift; flag specifics, redraft from guidelines

For guideline changes: Luka proposes via a `/decisions/` entry; the Founder approves before guidelines update.

## Versioning
- **v0** — June 2026. Directional, opinionated, refinable. Built to be argued with.
- **v1** — to follow once v0 has been exercised on 5+ real **external** assets.
  ⚠️ **Correctly blocked, not overdue.** Nothing external has shipped — the launch-gate holds every
  outward surface (`processes/launch-gate.md`), so the counter is at **zero by design**, not by neglect.
  The staged site, the demos and the connector console are all built and unshipped; they do not count,
  because the point of the trigger is that v0 survives contact with a real audience. Clarified
  2026-08-23 — as written it read like a milestone slipping.
