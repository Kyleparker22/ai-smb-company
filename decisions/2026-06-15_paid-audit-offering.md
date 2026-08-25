# 2026-06-15 — Build the paid AI Audit (the diagnostic front door)

## Decision
Productize discovery into a **paid AI Audit**: a fixed-scope, ~1-week diagnostic that finds + dollar-quantifies a prospect's biggest bottleneck and hands them a prioritized AI-employee roadmap — **before** they commit to a build + retainer. It's the low-risk paid entry point for **cold/skeptical prospects**, and the fee **credits toward the build**. the Founder greenlit building it after two competitors (CharlieOS, and the original transcript idea) converged on a "diagnostic-first" front door.

## Why
- **A small first yes.** Cold SMB owners won't jump to a recurring retainer; they'll pay a little to learn where they're bleeding money. The diagnosis *is* the pitch.
- **Qualifies hard + funds discovery.** A payer is a real buyer; and it's discovery we'd do anyway, now self-funding.
- **Counter-positions the "install it, you run it" players** (CharlieOS) — we diagnose *your* dollars and then *operate* the fix, vs. a template you install and maintain.

## What got built
- **SOP** — `processes/audit-sop.md`: the diagnostic questions (money/time/breakage/readiness maps), the 4-axis bottleneck-scoring framework (Money × Frequency × Owner-drain × Fixability → heat), the meeting structure (intake → call 1 → analysis → call 2), and the bottleneck→agent mapping.
- **Deliverable template** — `clients/_yourco-template/audit-report/` (config-driven HTML like the demo-kit; Kimi fills the `AUDIT` object; print-to-PDF; ships with a landscaping sample).
- **Offer page** — `agents/webb/pages/yourco-site-v2/audit.html` (already existed, on-brand, **no prices**; added the intake CTA).
- **Pre-call intake form** — `agents/webb/pages/yourco-site-v2/audit-intake.html` (10-min questionnaire so the call starts warm; staged capture → CRM at launch).
- **Pricing** — `pricing/v0/audit.md` (Polo proposes; **no number on the website** — the Founder's call; fee credits the build).
- **Placement** — `02_delivery_loop.md` Stage 0.5; when an Audit converts, its findings *are* the discovery doc.

## Rules
- **No price on the website or in cold copy.** Polo locks the fee; it's covered on the intro call. Reilly/Michelle/Kimi say "a focused paid diagnostic, credited toward your build" — never a number.
- **Skip the Audit for hot warm-intros** (e.g. Sample Client) — no tollbooth in front of a ready buyer.
- **Honest diagnosis** — if AI can't meaningfully help, say so and don't sell (brand-protective; SOP guardrail).
- **Owner:** Kimi runs it, Polo prices it, the Founder approves each report.

## Status
Built + staged. Live when the website launches (offer page + intake are part of the site) — same launch-gate as everything external. Polo to lock the fee + credit window before first use.
