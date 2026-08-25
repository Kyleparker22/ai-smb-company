> ⚠️ **EXAMPLE OUTPUT — not yours.** This is one run of this loop from the company this
> template was extracted from, kept so you can see the shape of what the loop produces.
> The dates, numbers, and findings describe **someone else's business**. Delete this file
> the first time your own loop writes a real one.

# Brand Drift Audit — 2026-08

*Luka, Brand Custodian.* Window: 2026-07-04 → 2026-08-03. Source of truth: `brand/v0/brand-guidelines.md` (v0.5) + `brand/DESIGN.md`.
Prior run: `loops/brand-audit/2026-07-06.md` — "What I'd do differently next run" was left empty, so no the Founder feedback to apply.

## Verdict
Copy is clean again. **One structural finding**: both drift patterns named last month are unchanged a month later, and the three rulings that would close them were written *inside* last month's artifact instead of `/decisions/` — so nothing could act on them. That's the escalation the prior audit set as its own watch condition. Two new material items on live surfaces, both one-line fixes.

## Structural

**1. Audit → fix loop has no closure step**
- Rule: prior-audit watchdog — "unfixed 2 audits running → escalate."
- Pure white `#fff` as a card surface: **14 live pages, byte-identical to last month** (`glass-box.html:40,47,55`, `instant-employee.html:41,54,73,103,115`, `demos.html:48,59,79,103`, +10). Inline `<i>` emphasis: **5 live pages, unchanged** (`manifesto.html:122,137`, `compare.html:125`, `demos.html:148`, `demos-tier2.html:109`, `instant-employee.html:175,338`). Italic captions: **6 pages, unchanged.**
- Cause, not neglect: the fixes were gated on three unruled questions, and those proposals never left the audit artifact. Written properly this run → `decisions/2026-08-03_brand-update-italics-gradients-surface.md`. `DESIGN.md` still has no `--surface` token, so every new page still inherits `#fff`.
- New surfaces are hardening the unruled patterns: `_concepts/` (07-21 design direction) bakes in italic signatures (`concept-b.html:54,323`) and a decorative radial-gradient hero glow (`concept-c.html:57`) — a bigger cleanup if the flat ban is upheld later.

## Material

**2. Banned hype emoji on a live page**
- `try-to-break-it.html:171` → guidelines §Voice/Never: "Hype emoji (🚀💯🔥)."
- Before: `label:"🔥 Get abusive"` · After: `label:"Get abusive"` (or a neutral glyph). Functional label, but it's a named-banned emoji on a customer-facing surface.

**3. Brand mark capitalized in live customer copy**
- `instant-employee.html:244` → DESIGN.md §7 hard rule: "Lowercase `yourco` everywhere the mark appears."
- Before: "text messages from YourCo about my request" · After: "text messages from **yourco**". ("YourCo LLC" in `privacy.html` / `sms-terms.html` is the legal entity — correct as-is.)

## Cosmetic
- Capital-I "YourCo Ops" in the agent signature on ~10 `#all-yourco` digests (Charles, Atlas) — same mark rule, internal exposure only. Fix the signature string once at the source.
- Italics-as-emphasis is now also the default in Slack mrkdwn (`_The runtime is dark._`, `_$200/mo_) — Slack has `*bold*`; the rule says use weight.
- `index.html:22` CSS comment "YourCo brand."

## Clean
- **Content (`loops/content/2026-07-10`, `07-24`)** — on-voice. Tagline sealed verbatim on all eight drafts, em-dash cap held, no banned words, no asserted stats. Model output.
- **Slack `#all-yourco`** — status emoji only (✅⚠️🔴), none of the banned trio.
- **Gmail** — the connected mailbox is the Founder's personal account, not `founder@yourco.example.com`; 30 days of sent mail contains no yourco-brand copy. Nothing auditable.
- No client `weekly/` artifacts exist (still no live engagement).

## Watchdog notes
- **Volume:** zero assets queued for pre-ship review, second month running — Luka is still catching drift post-hoc, not at ship.
- **Aging stat:** `manifesto.html:137` cites Gartner, March 2025 — inside the 18-month window until ~Sept 2026, then it breaks the rule. Candidate invariant for `runtime/consistency-check.py`.

## What I'd do differently next run
(Empty — for the Founder to fill)
