# Webb changelog — Careers / "become a Sales Rep" page (2026-06-30)

New page: `agents/webb/pages/yourco-site-v2/_parked/careers.html` — a flexible "become an yourco Sales Rep / referral partner" opportunities page with a lead-capture form. Built on the staged site (nothing deployed until the launch gate).

## What it is
- **Hero:** "You make the intro. yourco does the rest." — work-as-much-or-as-little, no base/quota/boss, performance-only.
- **What the role is** (3 steps): you introduce → yourco audits/closes/builds/operates/owns → you earn monthly, hands-off, no technical skill.
- **How you earn** — 3 tier cards matching the locked referral v1: **Referrer 10% (1–4) · Senior 15% (5–9) · Partner 20% (10+)**, residual, whole-book escalator.
- **Why it's no-risk** + **who makes a great rep**.
- **Form** + earnings disclaimer + close CTA + footer (with a "Become a rep" link).

## Form wiring
Mirrors `audit-intake.html`: captures name · email · phone (optional) · "why you'd be a great rep / your network"; POSTs JSON to **`/api/rep-intake`** (`source: "rep-intake"`), try/catch so the staged no-backend state resolves; on submit shows an inline thank-you. Backend activates on deploy (staged, like the other capture forms).

## Compliance (verified)
- ✅ **Earnings disclaimer present** — "A note on earnings": rates are *illustrative of how commission is structured*, not a promise/projection; earnings depend on effort + clients brought/retained; "many reps may earn little or nothing"; no income guarantee.
- ✅ **No multi-level / downline economics** — counsel-gated, so kept off the public page (verified: zero downline math, percentages, or recruiting-for-income claims). Only a soft non-numeric "you can also grow a team" line.
- ✅ **No fabricated traction** — no testimonials, rep counts, or "$X/month" promises; honest early-stage tone.
- Brand: nav + footer copied verbatim, `site.css`, lowercase `yourco`, `founder@yourco.example.com`, Fraunces on the tier rates, premium polish.

## Follow-ups (not done here)
- **Site-wide nav link** to `/careers` (only careers.html's own footer links it today; adding it to all ~20 pages' nav/footer is a separate sweep).
- **`/api/rep-intake` backend** — stand up on deploy so applicants land in the CRM (like audit-intake).
- **Counsel gate (Ray):** the rep economics + the held-back multi-level override must clear counsel before this page is published/promoted (`decisions/2026-06-30_referral-program-v1.md`).
